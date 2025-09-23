#!/usr/bin/env python3
"""
Stage 3: Commits and History
Implements commit objects that tie trees to history, creating a timeline of changes.
"""

import os
from pathlib import Path
import fire
from stage1_object_store import GitObjectStore
from stage2_blobs_and_trees import GitTreeBuilder
from static import GIT_DIR
import time
from datetime import datetime, timezone

class GitCommits:
    """Handles creation and parsing of Git commit objects."""

    def __init__(self, store: GitObjectStore):
        self.store = store

    def create_commit(self, tree_hash: str, parent_hash: str | None, message: str) -> str:
        """Create a commit object and store it."""
        # For simplicity, we'll use hardcoded author/committer details
        author_name = "Peter Norvig"
        author_email = "norvig@google.com"
        # Get current time in Git's expected format (Unix timestamp + timezone)
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp())
        offset = now.utcoffset().total_seconds()
        tz_str = f"{int(offset // 3600):+03d}{int((offset % 3600) // 60):02d}"

        author = f"author {author_name} <{author_email}> {timestamp} {tz_str}"
        committer = f"committer {author_name} <{author_email}> {timestamp} {tz_str}"

        lines = [f"tree {tree_hash}"]
        if parent_hash:
            lines.append(f"parent {parent_hash}")
        lines.append(author)
        lines.append(committer)
        lines.append("")  # Blank line before message
        lines.append(message)

        content = "\n".join(lines).encode('utf-8')
        commit_hash = self.store.store_object('commit', content)
        return commit_hash

    def parse_commit(self, commit_hash: str) -> dict:
        """Parse a commit object's content."""
        obj_type, content = self.store.retrieve_object(commit_hash)
        if obj_type != 'commit':
            raise ValueError(f"Object {commit_hash} is not a commit")

        headers, message = content.decode('utf-8').split('\n\n', 1)
        commit_data = {'message': message.strip()}

        for line in headers.split('\n'):
            key, value = line.split(' ', 1)
            if key in ['author', 'committer']:
                # For simplicity, just store the raw line
                commit_data[key] = value
            else:
                commit_data[key] = value

        return commit_data


class PyGitCommit:
    """CLI for Git commit operations."""

    def __init__(self, git_dir: str = GIT_DIR):
        self.store = GitObjectStore(git_dir)
        self.commits = GitCommits(self.store)
        self.builder = GitTreeBuilder(self.store)

    def write_tree(self, directory: str = '.') -> str:
        """Create tree object from directory."""
        try:
            tree_hash = self.builder.create_tree_from_directory(Path(directory))
            if tree_hash is None:
                print("Error: Cannot create tree from empty directory")
                return None
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

    def init(self):
        """Initialize empty Git repository."""
        self.store.git_dir.mkdir(exist_ok=True)
        print(f"Initialized empty Git repository in {self.store.git_dir.absolute()}")

    def commit_tree(self, tree_hash: str, p: str = None, m: str = "Test commit") -> str:
        """Create a new commit object."""
        try:
            commit_hash = self.commits.create_commit(tree_hash, p, m)
            return commit_hash
        except Exception as e:
            print(f"Error: {e}")
            return None

    def log(self, commit_hash: str):
        """Show commit logs starting from a given commit."""
        try:
            current_hash = commit_hash
            while current_hash:
                commit_data = self.commits.parse_commit(current_hash)

                print(f"commit {current_hash}")
                if 'author' in commit_data:
                    print(f"Author: {commit_data['author']}")
                if 'committer' in commit_data:
                    print(f"Date:   {commit_data['committer'].split('>')[1].strip()}") # A bit hacky, but works for this stage
                print("\n    " + commit_data['message'].replace('\n', '\n    '))
                print()

                current_hash = commit_data.get('parent')

        except Exception as e:
            print(f"Error: {e}")

    # Include other commands for a complete experience at this stage
    def hash_object(self, filename: str):
        """Delegate to object store."""
        try:
            content = Path(filename).read_bytes()
            sha1 = self.store.store_object('blob', content)
            return sha1
        except FileNotFoundError:
            print(f"Error: file '{filename}' not found.")

    def cat_file(self, sha1_hash: str):
        """Delegate to object store."""
        try:
            obj_type, content = self.store.retrieve_object(sha1_hash)
            print(content.decode('utf-8', errors='ignore'), end='')
        except FileNotFoundError:
            print(f"Error: object '{sha1_hash}' not found.")


if __name__ == '__main__':
    fire.Fire(PyGitCommit)
