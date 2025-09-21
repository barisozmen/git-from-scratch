#!/usr/bin/env python3
"""
Stage 1: Content-Addressable Object Store
A minimal implementation of Git's object storage system.

This demonstrates Git's core insight: content-addressable storage where
the SHA-1 hash of content becomes its immutable identifier.
"""

import hashlib
import zlib
import os
from pathlib import Path
import fire
from static import GIT_DIR


class GitObjectStore:
    """A content-addressable object store, the heart of Git."""
    
    def __init__(self, git_dir=GIT_DIR):
        self.git_dir = Path(git_dir)
        self.objects_dir = self.git_dir / 'objects'
        self.objects_dir.mkdir(parents=True, exist_ok=True)
    
    def _object_path(self, sha1_hash: str) -> Path:
        """Convert SHA-1 hash to filesystem path with sharding."""
        return self.objects_dir / sha1_hash[:2] / sha1_hash[2:]
    
    def _hash_content(self, obj_type: str, content: bytes) -> str:
        """Calculate Git's SHA-1 hash for content with proper header."""
        # Git's secret sauce: prepend type and size header
        header = f"{obj_type} {len(content)}\0".encode()
        full_content = header + content
        return hashlib.sha1(full_content).hexdigest()
    
    def store_object(self, obj_type: str, content: bytes) -> str:
        """Store content in the object store, return its SHA-1 hash."""
        sha1_hash = self._hash_content(obj_type, content)
        obj_path = self._object_path(sha1_hash)
        
        if not obj_path.exists():
            obj_path.parent.mkdir(exist_ok=True)
            # Git compresses objects to save space
            compressed = zlib.compress(f"{obj_type} {len(content)}\0".encode() + content)
            obj_path.write_bytes(compressed)
        
        return sha1_hash
    
    def retrieve_object(self, sha1_hash: str) -> tuple[str, bytes]:
        """Retrieve object by hash, return (type, content) tuple."""
        obj_path = self._object_path(sha1_hash)
        
        if not obj_path.exists():
            raise FileNotFoundError(f"Object {sha1_hash} not found")
        
        # Decompress and split header from content
        raw_data = zlib.decompress(obj_path.read_bytes())
        header, content = raw_data.split(b'\0', 1)
        obj_type, size_str = header.decode().split(' ')
        
        if len(content) != int(size_str):
            raise ValueError(f"Object {sha1_hash} corrupted: size mismatch")
        
        return obj_type, content


class PyGit:
    """Elegant CLI for Git from scratch using Fire."""
    
    def __init__(self, git_dir: str = GIT_DIR):
        self.store = GitObjectStore(git_dir)
    
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


if __name__ == '__main__':
    fire.Fire(PyGit)
