# Build Git From Scratch: A Progressive Course Plan

*A comprehensive course structure for building a minimal but functional Git implementation in Python*

Based on the excellent "Plumber's Guide to Git," this course teaches Git internals by building a working version control system from first principles. Each stage builds upon the previous and results in a working system that students can immediately test and use.

## Course Overview

By the end of this course, students will have built `pygit` - a minimal but functional Git implementation that covers all core Git concepts and can handle real version control workflows.

---

## **Stage 1: Content-Addressable Object Store**
**Duration**: 2 hours  
**Goal**: Create the foundation - a system that can store and retrieve file contents by their SHA-1 hash.

### What Students Build:
- Basic `.git/objects` directory structure
- SHA-1 hashing with proper Git headers (`blob <size>\0<content>`)
- Object storage with directory sharding (first 2 chars as subdirectory)
- Blob object creation and retrieval
- Zlib compression for storage efficiency

### Working System Result:
Students have a `pygit` command that can:
- `pygit hash-object <file>` - Store file content and return SHA-1
- `pygit cat-file <hash>` - Retrieve and display stored content
- Show that identical content gets identical hashes (deduplication)
- Demonstrate content-addressable storage principles

### Key Learning:
- Content-addressable storage concept
- SHA-1 hashing fundamentals  
- File system organization strategies
- Object immutability principles
- Why Git is fundamentally a key-value store

### Implementation Notes:
```python
# Core concepts to implement:
# - SHA1 hash calculation with Git headers
# - Object directory structure (.git/objects/ab/cdef...)
# - Zlib compression/decompression
# - File I/O operations
```

---

## **Stage 2: Blobs and Trees**
**Duration**: 3 hours  
**Goal**: Add directory structure support by implementing tree objects that reference blobs and other trees.

### What Students Build:
- Tree object format (permissions, type, hash, filename)
- Directory traversal and tree construction
- Recursive tree parsing and reconstruction
- File permission handling (644 vs 755)

### Working System Result:
Students can now:
- `pygit write-tree` - Create tree objects from directory structure
- `pygit read-tree <tree-hash>` - Recreate directory structure from tree
- Store and retrieve entire directory snapshots
- Handle nested directories and complex structures

### Key Learning:
- Hierarchical data structures in Git
- How Git represents directories and file permissions
- Recursive object relationships
- Complete repository snapshots
- Why Git doesn't store empty directories

### Implementation Notes:
```python
# Tree object format:
# <mode> <type> <hash>\t<filename>\n
# Example: "100644 blob a1b2c3...\tREADME.md\n"
```

---

## **Stage 3: Commits and History**
**Duration**: 3 hours  
**Goal**: Add context and history by implementing commit objects that reference trees and parent commits.

### What Students Build:
- Commit object format (tree ref, parent ref, author, committer, message)
- Commit creation with proper metadata (timestamps, timezone)
- History traversal (following parent links)
- Basic log functionality with pretty printing

### Working System Result:
Students can:
- `pygit commit-tree <tree-hash> [-p parent] -m "message"` - Create commits
- `pygit log <commit-hash>` - Show commit history
- Create linear histories of repository changes
- Include author information and timestamps

### Key Learning:
- How Git builds project history
- Metadata importance (author, timestamp, messages)
- Parent-child relationships in version control
- Linear vs. branching histories
- Unix timestamp and timezone handling

### Implementation Notes:
```python
# Commit object format:
# tree <tree-hash>
# parent <parent-hash>  (optional, can have multiple)
# author <name> <email> <timestamp> <timezone>
# committer <name> <email> <timestamp> <timezone>
# 
# <commit message>
```

---

## **Stage 4: References and Branches**
**Duration**: 2.5 hours  
**Goal**: Add human-friendly names for commits through the ref system.

### What Students Build:
- `.git/refs/heads/` directory structure
- Reference creation and updates
- HEAD reference and current branch tracking
- Basic branch operations and symbolic refs

### Working System Result:
Students can:
- `pygit update-ref refs/heads/main <commit-hash>` - Create branches
- `pygit branch` - List branches with current branch indicator
- `pygit checkout <branch>` - Switch branches (HEAD manipulation)
- Use branch names instead of commit hashes in all commands

### Key Learning:
- References as pointers to commits
- Branch mechanics in Git
- HEAD concept and current branch
- Why "branches are cheap" in Git
- Symbolic references vs direct references

### Implementation Notes:
```python
# HEAD file contains: "ref: refs/heads/main"
# Branch files contain: commit hash
# Symbolic ref resolution chain
```

---

## **Stage 5: Working Directory Operations**
**Duration**: 3.5 hours  
**Goal**: Connect Git's internal structure to the working directory with checkout and status.

### What Students Build:
- Working directory scanning and file discovery
- File status comparison (modified, added, deleted)
- Tree checkout to working directory
- Basic diff functionality (line-by-line comparison)
- File metadata tracking (mtime, size)

### Working System Result:
Students can:
- `pygit status` - Show working directory changes
- `pygit checkout <branch>` - Update working directory from branch
- `pygit diff` - Show differences between versions
- Handle file modifications, additions, and deletions

### Key Learning:
- Three-way relationship: working dir, staging, and repository
- File system interaction and monitoring
- Change detection algorithms
- Working tree vs. repository state
- File metadata and change detection optimization

---

## **Stage 6: Index/Staging Area**
**Duration**: 4 hours  
**Goal**: Implement Git's staging area for selective commits.

### What Students Build:
- `.git/index` file format and management
- Staging area operations (add, remove, update)
- Integration between working directory, index, and repository
- Index-based status reporting

### Working System Result:
Students can:
- `pygit add <file>` - Stage changes
- `pygit commit -m "message"` - Commit staged changes
- `pygit reset <file>` - Unstage changes
- Full Git workflow: modify → add → commit

### Key Learning:
- Three-stage Git architecture (working/staging/repository)
- Selective commit preparation
- Index as temporary storage and optimization layer
- Complete Git workflow understanding
- Why staging area exists (partial commits, review before commit)

### Implementation Notes:
```python
# Index file format (simplified):
# - File path
# - Object hash
# - File metadata (mtime, size, etc.)
# - Stage number (0 = normal, 1-3 = conflict stages)
```

---

## **Stage 7: Basic Merging**
**Duration**: 4 hours  
**Goal**: Implement simple merge functionality to combine branches.

### What Students Build:
- Three-way merge algorithm (common ancestor, ours, theirs)
- Merge commit creation (multiple parents)
- Basic conflict detection and marking
- Fast-forward merge optimization

### Working System Result:
Students can:
- `pygit merge <branch>` - Merge branches
- Handle simple merge scenarios automatically
- Create merge commits with multiple parents
- Detect basic merge conflicts

### Key Learning:
- Merge strategies and algorithms
- Multiple parent commits (octopus merges)
- Conflict resolution concepts
- Distributed development workflows
- Common ancestor finding algorithms

---

## **Stage 8: Integration and Polish**
**Duration**: 2 hours  
**Goal**: Create a cohesive CLI tool and connect all components.

### What Students Build:
- Unified command-line interface with proper argument parsing
- Git repository initialization (`pygit init`)
- Comprehensive error handling and user feedback
- Configuration system (user.name, user.email)
- Help system and command documentation

### Working System Result:
Students have a complete `pygit` tool that can:
- `pygit init` - Initialize repositories
- `pygit add`, `pygit commit`, `pygit branch`, `pygit merge`
- `pygit log`, `pygit status`, `pygit diff`, `pygit checkout`
- Handle real-world Git workflows with proper error messages

### Key Learning:
- System integration principles
- User interface design for developer tools
- Error handling in complex systems
- Production-ready code practices
- CLI best practices

---

## **Pedagogical Approach**

Each stage follows this proven pattern:

### 1. **Theory Introduction** (15 minutes)
- Explain the concept and motivation
- Show how it fits into Git's overall architecture
- Discuss why this component is necessary

### 2. **Live Demo** (10 minutes)  
- Demonstrate the target functionality working
- Show real Git commands that relate to what we're building
- Connect to students' existing Git knowledge

### 3. **Guided Implementation** (45-60 minutes)
- Students code the feature step-by-step
- Provide code scaffolding and key insights
- Debug common issues together

### 4. **Testing and Verification** (15 minutes)
- Test the implementation thoroughly
- Compare behavior with real Git where applicable
- Ensure the working system meets objectives

### 5. **Reflection and Discussion** (15 minutes)
- Review what was learned and how it connects
- Discuss edge cases and real-world considerations  
- Preview the next stage

## **Prerequisites**

- **Python Knowledge**: Intermediate level (classes, file I/O, basic algorithms)
- **Command Line**: Comfortable with terminal/shell usage
- **Git Experience**: Basic Git usage (add, commit, branch, merge)
- **System Concepts**: Basic understanding of file systems and hashing

## **Key Benefits of This Structure**

- **Progressive Complexity**: Each stage builds naturally on the previous
- **Always Working**: Students see concrete results immediately at each stage  
- **Complete Understanding**: Covers all core Git concepts from first principles
- **Practical Results**: Creates a real (if minimal) version control system
- **Extensible Foundation**: Easy to add advanced features later
- **Industry Relevant**: Deep understanding of tools used daily by developers

## **Extensions and Advanced Topics**

After completing the core course, advanced students can explore:

- **Remote Repositories**: Push/pull protocols and network communication
- **Pack Files**: Efficient storage and transfer of Git objects
- **Advanced Merging**: Recursive merge strategies and complex conflict resolution
- **Hooks**: Event-driven automation and workflow integration
- **Performance**: Optimizations for large repositories
- **Git Protocols**: HTTP, SSH, and Git native protocols

## **Assessment Ideas**

- **Code Review**: Students review each other's implementations
- **Feature Addition**: Add a new Git command (like `pygit tag`)
- **Performance Analysis**: Profile and optimize their implementation
- **Comparison Study**: Compare their implementation with real Git behavior
- **Documentation**: Write comprehensive documentation for their `pygit` tool

---

This course structure ensures students gain deep, practical understanding of Git internals while building something genuinely useful that demonstrates their mastery of version control concepts!
