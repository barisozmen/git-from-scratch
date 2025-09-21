#!/usr/bin/env python3
"""
Stage 2: Blobs and Trees
Extends Stage 1 with tree objects that capture directory structure and filenames.

Trees are Git's way of storing directory snapshots - they reference blobs (files)
and other trees (subdirectories), creating a complete filesystem representation.
"""

import os
import stat
from pathlib import Path
import fire
from stage1_object_store import GitObjectStore
from static import GIT_DIR


class GitTreeBuilder:
    """Builds tree objects from directory structure."""
    
    def __init__(self, store: GitObjectStore):
        self.store = store
    
    def _get_file_mode(self, filepath: Path) -> str:
        """Get Git file mode (permissions) for a file."""
        file_stat = filepath.stat()
        if stat.S_ISDIR(file_stat.st_mode):
            return '40000'  # Directory
        elif file_stat.st_mode & stat.S_IXUSR:
            return '100755'  # Executable file
        else:
            return '100644'  # Regular file
    
    def _build_tree_content(self, entries: list[tuple[str, str, str]]) -> bytes:
        """Build tree object content from sorted entries."""
        content = b''
        for mode, obj_type, obj_hash, name in sorted(entries, key=lambda x: x[3]):
            # Git tree format: "<mode> <name>\0<20-byte-hash>"
            entry = f"{mode} {name}\0".encode()
            # Convert hex hash to binary
            hash_bytes = bytes.fromhex(obj_hash)
            content += entry + hash_bytes
        return content
    
    def create_tree_from_directory(self, directory: Path = Path('.')) -> str:
        """Create a tree object from directory contents."""
        if directory.name == GIT_DIR:
            return None  # Skip .git directory
        
        entries = []
        
        for item in sorted(directory.iterdir()):
            if item.name.startswith('.'):
                continue  # Skip hidden files for now
            
            if item.is_file():
                # Store file as blob
                content = item.read_bytes()
                blob_hash = self.store.store_object('blob', content)
                mode = self._get_file_mode(item)
                entries.append((mode, 'blob', blob_hash, item.name))
            
            elif item.is_dir():
                # Recursively create tree for subdirectory
                subtree_hash = self.create_tree_from_directory(item)
                if subtree_hash:  # Only add if subdirectory had contents
                    entries.append(('40000', 'tree', subtree_hash, item.name))
        
        if not entries:
            return None  # Empty directory
        
        # Create tree object
        tree_content = self._build_tree_content(entries)
        return self.store.store_object('tree', tree_content)
    
    def read_tree_to_directory(self, tree_hash: str, target_dir: Path = Path('.')) -> None:
        """Recreate directory structure from tree object."""
        obj_type, content = self.store.retrieve_object(tree_hash)
        
        if obj_type != 'tree':
            raise ValueError(f"Object {tree_hash} is not a tree")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse tree content
        offset = 0
        while offset < len(content):
            # Find the null byte that separates mode+name from hash
            null_pos = content.find(b'\0', offset)
            if null_pos == -1:
                break
            
            # Parse mode and name
            mode_name = content[offset:null_pos].decode()
            mode, name = mode_name.split(' ', 1)
            
            # Extract 20-byte hash
            hash_bytes = content[null_pos + 1:null_pos + 21]
            obj_hash = hash_bytes.hex()
            
            file_path = target_dir / name
            
            if mode == '40000':  # Directory
                self.read_tree_to_directory(obj_hash, file_path)
            else:  # File
                _, file_content = self.store.retrieve_object(obj_hash)
                file_path.write_bytes(file_content)
                
                # Set executable permission if needed
                if mode == '100755':
                    file_path.chmod(0o755)
                else:
                    file_path.chmod(0o644)
            
            offset = null_pos + 21


class PyGitTree:
    """Elegant CLI for Git trees using Fire."""
    
    def __init__(self, git_dir: str = GIT_DIR):
        self.store = GitObjectStore(git_dir)
        self.builder = GitTreeBuilder(self.store)
    
    def init(self):
        """Initialize empty Git repository."""
        self.store.git_dir.mkdir(exist_ok=True)
        print(f"Initialized empty Git repository in {self.store.git_dir.absolute()}")
    
    def hash_object(self, filename: str) -> str:
        """Store file content, return hash."""
        try:
            content = Path(filename).read_bytes()
            sha1_hash = self.store.store_object('blob', content)
            print(sha1_hash)
            return sha1_hash
        except FileNotFoundError:
            print(f"Error: file '{filename}' not found")
            return None
    
    def cat_file(self, sha1_hash: str):
        """Retrieve and display object content."""
        try:
            obj_type, content = self.store.retrieve_object(sha1_hash)
            if obj_type == 'blob':
                print(content.decode('utf-8'), end='')
            else:
                print(f"Object type: {obj_type}")
                print(content.decode('utf-8'))
        except FileNotFoundError:
            print(f"Error: object '{sha1_hash}' not found")
    
    def write_tree(self, directory: str = '.') -> str:
        """Create tree object from directory."""
        try:
            tree_hash = self.builder.create_tree_from_directory(Path(directory))
            if tree_hash is None:
                print("Error: Cannot create tree from empty directory")
                return None
            print(tree_hash)
            return tree_hash
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def read_tree(self, tree_hash: str, target_dir: str = 'restored'):
        """Recreate directory from tree object."""
        try:
            self.builder.read_tree_to_directory(tree_hash, Path(target_dir))
            print(f"Tree {tree_hash} restored to {target_dir}")
        except Exception as e:
            print(f"Error: {e}")
    
    def ls_tree(self, tree_hash: str):
        """List contents of tree object."""
        try:
            obj_type, content = self.store.retrieve_object(tree_hash)
            
            if obj_type != 'tree':
                print(f"Error: Object {tree_hash} is not a tree")
                return
            
            # Parse and display tree entries
            offset = 0
            while offset < len(content):
                null_pos = content.find(b'\0', offset)
                if null_pos == -1:
                    break
                
                mode_name = content[offset:null_pos].decode()
                mode, name = mode_name.split(' ', 1)
                
                hash_bytes = content[null_pos + 1:null_pos + 21]
                obj_hash = hash_bytes.hex()
                
                obj_type_display = 'tree' if mode == '40000' else 'blob'
                print(f"{mode} {obj_type_display} {obj_hash}\t{name}")
                offset = null_pos + 21
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    fire.Fire(PyGitTree)
