#!/usr/bin/env python3
"""
Demo: Stages 1 & 2 - Object Store and Trees
Demonstrates the elegant architecture of Git's content-addressable storage.

This script shows how Git's fundamental insight - content-addressed storage
with SHA-1 hashing - enables powerful version control capabilities.
"""

import tempfile
import shutil
from pathlib import Path
from stage1_object_store import GitObjectStore, PyGit
from stage2_blobs_and_trees import GitTreeBuilder, PyGitTree


def demo_stage1_object_store():
    """Demonstrate Stage 1: Content-addressable object store."""
    print("=" * 60)
    print("STAGE 1 DEMO: Content-Addressable Object Store")
    print("=" * 60)
    
    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        store = GitObjectStore(workspace / '.git')
        
        print(f"Working in: {workspace}")
        
        # Create some files
        (workspace / 'hello.txt').write_text("Hello, Git from scratch!")
        (workspace / 'world.txt').write_text("Hello, Git from scratch!")  # Same content!
        (workspace / 'different.txt').write_text("This is different content.")
        
        print("\n1. Storing files as blobs:")
        
        # Store files and show hashes
        hash1 = store.store_object('blob', (workspace / 'hello.txt').read_bytes())
        hash2 = store.store_object('blob', (workspace / 'world.txt').read_bytes())
        hash3 = store.store_object('blob', (workspace / 'different.txt').read_bytes())
        
        print(f"   hello.txt     -> {hash1}")
        print(f"   world.txt     -> {hash2}")
        print(f"   different.txt -> {hash3}")
        
        print(f"\n2. Key insight: Identical content = identical hash!")
        print(f"   hash1 == hash2: {hash1 == hash2}")
        
        print(f"\n3. Content is preserved perfectly:")
        obj_type, content = store.retrieve_object(hash1)
        print(f"   Retrieved: '{content.decode()}'")
        
        print(f"\n4. Object store structure:")
        for obj_file in sorted(workspace.glob('.git/objects/*/*')):
            rel_path = obj_file.relative_to(workspace)
            print(f"   {rel_path}")


def demo_stage2_trees():
    """Demonstrate Stage 2: Trees for directory structure."""
    print("\n" + "=" * 60)
    print("STAGE 2 DEMO: Trees and Directory Structure")
    print("=" * 60)
    
    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        store = GitObjectStore(workspace / '.git')
        builder = GitTreeBuilder(store)
        
        print(f"Working in: {workspace}")
        
        # Create a more complex directory structure
        (workspace / 'README.md').write_text("# My Project\nThis is awesome!")
        (workspace / 'src').mkdir()
        (workspace / 'src' / 'main.py').write_text("print('Hello, World!')")
        (workspace / 'src' / 'utils.py').write_text("def helper(): pass")
        (workspace / 'docs').mkdir()
        (workspace / 'docs' / 'guide.txt').write_text("User guide goes here")
        
        print("\n1. Directory structure created:")
        for item in sorted(workspace.rglob('*')):
            if item.is_file() and '.git' not in str(item):
                rel_path = item.relative_to(workspace)
                print(f"   {rel_path}")
        
        print("\n2. Creating tree objects:")
        tree_hash = builder.create_tree_from_directory(workspace)
        print(f"   Root tree: {tree_hash}")
        
        print(f"\n3. Tree content (like 'git ls-tree'):")
        obj_type, content = store.retrieve_object(tree_hash)
        
        # Parse and display tree entries nicely
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
            print(f"   {mode} {obj_type_display} {obj_hash} {name}")
            offset = null_pos + 21
        
        print(f"\n4. Complete object store:")
        for obj_file in sorted(workspace.glob('.git/objects/*/*')):
            rel_path = obj_file.relative_to(workspace)
            obj_hash = rel_path.parent.name + rel_path.name
            obj_type, _ = store.retrieve_object(obj_hash)
            print(f"   {rel_path} ({obj_type})")
        
        print(f"\n5. Recreating directory from tree:")
        restore_dir = workspace / 'restored_from_tree'
        builder.read_tree_to_directory(tree_hash, restore_dir)
        
        print(f"   Restored files:")
        for item in sorted(restore_dir.rglob('*')):
            if item.is_file():
                rel_path = item.relative_to(restore_dir)
                print(f"   {rel_path}")
        
        print(f"\n6. Verification: Original vs Restored")
        original_readme = (workspace / 'README.md').read_text()
        restored_readme = (restore_dir / 'README.md').read_text()
        print(f"   README.md identical: {original_readme == restored_readme}")


def demo_git_insight():
    """Demonstrate the key insight that makes Git powerful."""
    print("\n" + "=" * 60)
    print("THE KEY INSIGHT: Content-Addressable Everything!")
    print("=" * 60)
    
    print("""
Git's genius is treating everything as content-addressable objects:

🔹 BLOBS store file content (but not filenames)
🔹 TREES store directory structure (filenames + blob/tree references)  
🔹 Both get SHA-1 hashes based on their content
🔹 Identical content = identical hash = automatic deduplication
🔹 Immutable objects = safe sharing and referencing

This creates a Merkle tree where:
• Every object is verified by its hash
• Any change bubbles up through parent hashes  
• Complete integrity checking is built-in
• Sharing and caching are automatic

Next stages will add COMMITS (context + history) and REFS (human names)!
""")


if __name__ == '__main__':
    print("🚀 Build Git From Scratch - Stages 1 & 2 Demo")
    print("Elegant code demonstrating Git's fundamental architecture\n")
    
    demo_stage1_object_store()
    demo_stage2_trees()
    demo_git_insight()
    
    print("\n" + "=" * 60)
    print("🎉 Demo complete! Try the commands yourself:")
    print("   python stage1_object_store.py --help")
    print("   python stage2_blobs_and_trees.py --help")
    print("=" * 60)
