#!/usr/bin/env python3
"""
Stage 4: References and Branches
Adds human-friendly names for commits using references (refs),
which are pointers to commits, forming the basis of branches.
"""
import os
from pathlib import Path
import fire
from stage1_object_store import GitObjectStore
from stage3_commits_and_history import GitCommits, PyGitCommit
from static import GIT_DIR

class GitRefs:
    """Manages Git references like branches and HEAD."""

    def __init__(self, git_dir: str = GIT_DIR):
        self.git_dir = Path(git_dir)
        self.refs_dir = self.git_dir / 'refs'
        self.heads_dir = self.refs_dir / 'heads'
        self.head_file = self.git_dir / 'HEAD'

    def update_ref(self, ref_name: str, commit_hash: str, symbolic: bool = False):
        """Update a ref to point to a commit hash or another ref."""
        # Ensure parent directories exist
        ref_path = self.git_dir / ref_name
        ref_path.parent.mkdir(parents=True, exist_ok=True)

        if symbolic:
            # For symbolic refs, the second argument is the target ref name
            content = f"ref: {commit_hash}"
        else:
            # For direct refs like branches, store the commit hash
            content = commit_hash

        ref_path.write_text(content.strip() + '\n')
        print(f"Updated ref '{ref_name}' to point to '{content.strip()}'")

    def resolve_ref(self, ref_name: str) -> str | None:
        """Resolve a ref name to a commit hash."""
        if ref_name == 'HEAD' and not self.head_file.exists():
            return None # HEAD doesn't exist yet

        ref_path = self.git_dir / ref_name

        if not ref_path.exists():
            # Maybe it's a short branch name? Try refs/heads/
            ref_path = self.heads_dir / ref_name
            if not ref_path.exists():
                return None # Not found

        content = ref_path.read_text().strip()

        # Is it a symbolic ref?
        if content.startswith('ref: '):
            return self.resolve_ref(content.split(' ', 1)[1])
        else:
            # It's a direct ref (contains a hash)
            return content

    def get_head_commit(self) -> str | None:
        """Get the commit hash that HEAD points to."""
        return self.resolve_ref('HEAD')

    def list_branches(self):
        """List all branches."""
        branches = []
        if self.heads_dir.exists():
            for branch_file in self.heads_dir.iterdir():
                branches.append(branch_file.name)
        return branches

    def get_current_branch(self) -> str | None:
        """Get the name of the current branch from HEAD."""
        if not self.head_file.exists():
            return None

        content = self.head_file.read_text().strip()
        if content.startswith('ref: refs/heads/'):
            return content.split('/')[-1]
        return None # Detached HEAD state


class PyGitRef(PyGitCommit):
    """CLI extending commit commands with refs and branches."""

    def __init__(self, git_dir: str = GIT_DIR):
        super().__init__(git_dir)
        self.refs = GitRefs(git_dir)

    def update_ref(self, ref_name: str, commit_hash: str):
        """Update a ref to point to a commit hash."""
        # A simple safety check
        if len(commit_hash) != 40 or not all(c in '0123456789abcdef' for c in commit_hash):
             print(f"Error: '{commit_hash}' is not a valid SHA-1 hash.")
             return
        self.refs.update_ref(ref_name, commit_hash)

    def branch(self, branch_name: str = None, start_point: str = 'HEAD'):
        """List branches or create a new one."""
        if not branch_name:
            # List branches
            current_branch = self.refs.get_current_branch()
            for b in self.refs.list_branches():
                if b == current_branch:
                    print(f"* {b}")
                else:
                    print(f"  {b}")
        else:
            # Create a new branch
            commit_hash = self.refs.resolve_ref(start_point)
            if not commit_hash:
                print(f"Error: Cannot resolve '{start_point}' to a commit.")
                return
            self.refs.update_ref(f"refs/heads/{branch_name}", commit_hash)
            print(f"Branch '{branch_name}' created at '{commit_hash[:7]}'")

    def checkout(self, branch_name: str):
        """Switch branches by updating HEAD."""
        # Check if branch exists
        commit_hash = self.refs.resolve_ref(f"refs/heads/{branch_name}")
        if not commit_hash:
            print(f"Error: branch '{branch_name}' not found.")
            return

        # Update HEAD to point to the new branch
        self.refs.update_ref('HEAD', f"refs/heads/{branch_name}", symbolic=True)
        print(f"Switched to branch '{branch_name}'")

    def log(self, start_point: str = 'HEAD'):
        """Show commit logs starting from a ref or commit."""
        commit_hash = self.refs.resolve_ref(start_point)
        if not commit_hash:
            print(f"Error: Cannot resolve '{start_point}' to a commit.")
            return
        super().log(commit_hash)

    def init(self):
        """Initialize a new repository."""
        super().init()
        # Set up the initial HEAD to point to main
        self.refs.update_ref('HEAD', 'refs/heads/main', symbolic=True)
        print("Set HEAD to point to 'main'")


if __name__ == '__main__':
    fire.Fire(PyGitRef)
