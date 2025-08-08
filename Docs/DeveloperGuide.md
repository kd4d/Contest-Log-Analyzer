# Developer Guide - Contest Log Analyzer

**Version: 0.31.1-Beta**
**Date: 2025-08-07**

---
### --- Revision History ---
## [0.31.1-Beta] - 2025-08-07
# - Reviewed and synchronized documentation with the v0.31.x codebase.
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
---

This guide outlines the development and release workflow for the Contest Log Analyzer.

### Standard Development Workflow

All new features, bug fixes, and other code changes should be committed to the `develop` branch.

1.  **Ensure you are on the `develop` branch:**

        git checkout develop

2.  **Do your work:** Modify, add, and delete files as needed.
3.  **Commit your changes:**

        # Add your changes to the staging area
        git add .
        
        # Commit the changes with a descriptive message
        git commit -m "A brief description of the work you did"
        
        # Push your commits to the remote develop branch
        git push origin develop

### Publishing a New Beta Release to Testers

When the code in the `develop` branch is stable, tested, and ready for a beta release, you merge it into the `main` branch. This makes it available to your testers.

1.  **Update the Revision History:** Before merging, update the `Revision History` section at the top of the `InstallationGuide.md` file with the new version number and changes.
2.  **Switch to the `master` branch:**

        git checkout master

3.  **Ensure `master` is up-to-date:**

        git pull origin master

4.  **Merge `develop` into `master`:** This brings all the stable, new code into the release branch.

        git merge develop

5.  **Push the `master` branch:** This publishes the new release.

        git push origin master

6.  **Switch back to `develop` to continue working:**

        git checkout develop

After this process, you can inform your beta testers that a new version is available. They can then run `git pull` to get the changes.

---
---

## Advanced Branch Management

### Archiving a Development Branch

Use this workflow when a development cycle is complete and you want to start a fresh `develop` branch from `master` while preserving the history of the old one.

1.  **Switch to `master`:**
    
        git checkout master

2.  **Rename the old `develop` branch:**
    
        git branch -m develop archive/develop-old

3.  **Create a new `develop` branch from `master`:**
    
        git checkout -b develop

4.  **Update the remote repository:**
    
        # Delete the old remote branch
        git push origin --delete develop
        
        # Push the new archived branch
        git push origin archive/develop-old
        
        # Push the new develop branch and set it to track
        git push -u origin develop

### Saving Uncommitted Work to a New Branch

Use this workflow when you have uncommitted changes on `master` (a "dirty" working directory) and want to move them to a new branch without affecting `master`.

1.  **Create and switch to the new branch:** (Your changes will come with you)
    
        git checkout -b <new-branch-name>

2.  **Stage all changes:**
    
        git add .

3.  **Commit the changes to the new branch:**
    
        git commit -m "Saving work-in-progress to new branch"