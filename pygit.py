#!/usr/bin/env python3
"""
Pygit: A minimal Git implementation in Python.

This tool combines all the plumbing commands from the previous stages
into a single, elegant CLI.
"""

import fire
from stage4_refs_and_branches import PyGitRef
from static import GIT_DIR

class GitPlumbing:
    """
    A collection of Git plumbing commands.

    This class uses composition to expose commands from the other stage files.
    """
    def __init__(self, git_dir: str = GIT_DIR):
        # We instantiate the final stage's class, which contains all the logic.
        # This is not ideal, as it pulls in all methods, but it's the simplest
        # way to expose them all without re-implementing them.
        self._cli = PyGitRef(git_dir)

    def init(self, *args, **kwargs):
        """Initialize a new repository."""
        return self._cli.init(*args, **kwargs)

    def hash_object(self, *args, **kwargs):
        """Store file content, return hash."""
        return self._cli.hash_object(*args, **kwargs)

    def cat_file(self, *args, **kwargs):
        """Retrieve and display object content."""
        return self._cli.cat_file(*args, **kwargs)

    def write_tree(self, *args, **kwargs):
        """Create tree object from directory."""
        return self._cli.write_tree(*args, **kwargs)

    def read_tree(self, *args, **kwargs):
        """Recreate directory from tree object."""
        return self._cli.read_tree(*args, **kwargs)

    def ls_tree(self, *args, **kwargs):
        """List contents of tree object."""
        return self._cli.ls_tree(*args, **kwargs)

    def commit_tree(self, *args, **kwargs):
        """Create a new commit object."""
        return self._cli.commit_tree(*args, **kwargs)

    def log(self, *args, **kwargs):
        """Show commit logs."""
        return self._cli.log(*args, **kwargs)

    def update_ref(self, *args, **kwargs):
        """Update a ref."""
        return self._cli.update_ref(*args, **kwargs)

    def branch(self, *args, **kwargs):
        """List or create branches."""
        return self._cli.branch(*args, **kwargs)

    def checkout(self, *args, **kwargs):
        """Switch branches."""
        return self._cli.checkout(*args, **kwargs)


if __name__ == '__main__':
    fire.Fire(GitPlumbing)
