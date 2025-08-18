Understood. Here is the updated `Docs/GitBranchInstructions.md` file, delivered in a plaintext block for correct copying.

```
# Git Feature Branch Workflow

**Version: 0.37.0-Beta**
**Date: 2025-08-18**

---
### --- Revision History ---
## [0.37.0-Beta] - 2025-08-18
### Added
# - Initial versioning of the document to align with project standards.
# - Added Section 7 to explain `git revert` for correcting mistakes.
# - Added Section 8 to explain file management with `.gitignore` and `git rm`.
---

The feature branch workflow is a standard practice that keeps your `master` branch clean and stable. It lets you work on new features in an isolated environment without affecting the main codebase. Once a feature is complete and tested, it's merged back into `master`. The Git commands are the same whether you're using Windows Shell (Command Prompt, PowerShell) or a Bash shell.
***

## 1. Start from `master`

Before you do anything, you need to make sure your local `master` branch is up-to-date with the remote repository (like GitHub or Azure DevOps).
```
# Switch to your master branch
git switch master

# Pull the latest changes from the remote server
git pull
```

***

## 2. Create and Switch to a Feature Branch

Now, you'll create a new branch for your feature. Branch names should be short and descriptive, like `login-form` or `user-profile-page`. This command creates a **new branch** and **immediately switches** to it.
```
# The -c flag stands for "create"
git switch -c new-feature-name
```

*You can now work safely on this branch. Think of it as a separate copy of the project where your changes won't affect anyone else until you're ready.*

***

## 3. Develop the Feature: Add and Commit

This is where you'll do your work—writing code, adding files, and fixing bugs. As you complete small, logical chunks of work, you should **commit** them. A commit is like a permanent save point. The process for each commit is the same:
1.  **Stage** your changes (`git add`).
2.  **Commit** them with a clear message (`git commit`).
```
# Stage a specific file
git add path/to/your/file.js

# Or stage all changed files in the project
git add .
# Commit the staged files with a descriptive message
git commit -m "feat: Add user login form component"
```

You can (and should) have many commits on your feature branch. Committing often creates a clear history of your work and makes it easier to undo changes if something goes wrong.
***

## 4. Keep Your Branch Synced (Optional but Recommended)

If you're working on a feature for a while, the `master` branch might get updated by your teammates. It's a good practice to pull those updates into your feature branch. This makes the final merge much easier.
```
# Fetch the latest changes from all remote branches
git fetch origin

# Re-apply your commits on top of the latest master branch
git rebase origin/master
```

The **`rebase`** command essentially "unplugs" your branch's changes, updates the base to the latest version of `master`, and then "re-plugs" your changes on top. This keeps your project history clean and linear.

***

## 5. Merge Your Feature into `master`

Once your feature is complete, tested, and ready to go, it's time to merge it back into the `master` branch.
```
# 1. First, go back to the master branch
git switch master

# 2. Make sure it's up-to-date one last time
git pull

# 3. Merge your feature branch into master
git merge --no-ff new-feature-name
```

Using **`--no-ff`** (no fast-forward) is a crucial best practice. It creates a "merge commit" that ties the history of your feature branch together. This makes it very easy to see when a specific feature was merged into `master` and which commits belonged to it.
***

## 6. Push and Clean Up

Your `master` branch now has the new feature, but only on your local machine. You need to push it to the remote server. After that, you can delete the feature branch, since its work is now part of `master`.
```
# 1. Push the updated master branch to the remote
git push origin master

# 2. Delete the local feature branch
git branch -d new-feature-name

# 3. Delete the remote feature branch
git push origin --delete new-feature-name
```

That's the complete lifecycle! 🚀 You've successfully created a feature, developed it in isolation, and safely merged it into the main project.
---
## 7. Correcting Mistakes (`git revert`)

Sometimes you commit a change that you later realize was a mistake. The safest way to undo a commit that has been shared is `git revert`. This command does not rewrite history; instead, it creates a *new commit* that is the exact inverse of the commit you want to undo.

```
# Find the hash of the commit you want to undo (e.g., from `git log`)
# Let's say the bad commit hash is `a1b2c3d4`

# Create a new commit that undoes the changes from the bad commit
git revert a1b2c3d4
```
---
## 8. Managing Files (`.gitignore` and `git rm`)

It's important to keep your repository clean of temporary or unnecessary files.

### Ignoring Untracked Files (`.gitignore`)
The best way to handle files that should *never* be in the repository (like build artifacts, log files, or local environment files) is to use a `.gitignore` file. This is a simple text file in the root of your project that tells Git which files or patterns to ignore. By adding patterns to `.gitignore`, these files won't show up in `git status` and cannot be accidentally committed.

### Removing Tracked Files (`git rm`)
If you have already committed a file that you now want to delete from the project, you must use `git rm`. This command removes the file from both your working directory and Git's tracking index.

```
# Remove a file that is already tracked by Git
git rm path/to/unwanted-file.txt

# Commit the deletion
git commit -m "fix: Remove obsolete file"
```

Use `git rm -f` if you have local modifications to the file that you want to discard along with the deletion.
```

Please respond with 'Acknowledged' to confirm.