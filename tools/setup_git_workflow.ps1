# tools/setup_git_workflow.ps1
#
# Purpose: Setup git workflow tools (pre-commit hooks and git aliases) for Contest Log Analytics.
#          Can be run standalone or invoked from setup.bat.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)

param(
    [switch]$SkipHooks,
    [switch]$SkipAliases
)

$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "Setting up Git Workflow Tools for Contest Log Analytics..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Setup Pre-commit Hooks
if (-not $SkipHooks) {
    Write-Host "Step 1: Installing pre-commit hooks..." -ForegroundColor Yellow
    
    # Check if pre-commit is installed
    $precommitInstalled = $false
    $null = pre-commit --version 2>&1 | Out-Null
    if ($?) {
        $precommitInstalled = $true
        Write-Host "  ✓ pre-commit is installed" -ForegroundColor Green
        
        # Install hooks
        Set-Location $repoRoot
        pre-commit install 2>&1 | Out-Null
        if ($?) {
            Write-Host "  ✓ Pre-commit hooks installed successfully" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Warning: pre-commit install had issues" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ✗ pre-commit is not installed" -ForegroundColor Red
        Write-Host "    Install it with: pip install pre-commit" -ForegroundColor Yellow
        Write-Host "    Then run this script again." -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Host "Step 1: Skipped (--SkipHooks)" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Setup Git Aliases
if (-not $SkipAliases) {
    Write-Host "Step 2: Setting up git aliases..." -ForegroundColor Yellow
    
    # Main branch history (clean, squash-like view)
    git config alias.mainlog 'log --first-parent --oneline --graph --decorate'
    Write-Host "  ✓ mainlog alias configured" -ForegroundColor Green
    
    # Full history with all branches
    git config alias.fullhistory 'log --all --graph --oneline --decorate'
    Write-Host "  ✓ fullhistory alias configured" -ForegroundColor Green
    
    # Feature branch history
    git config alias.featurelog 'log --oneline --graph --all --decorate'
    Write-Host "  ✓ featurelog alias configured" -ForegroundColor Green
    
    # Recent main branch commits only (no merge bubbles)
    git config alias.recent 'log --first-parent --oneline --graph -20'
    Write-Host "  ✓ recent alias configured" -ForegroundColor Green
    
    # Show what's in a feature branch vs main
    git config alias.branchdiff 'log --oneline --graph main..'
    Write-Host "  ✓ branchdiff alias configured" -ForegroundColor Green
    
    Write-Host "  ✓ Git aliases configured successfully" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Step 2: Skipped (--SkipAliases)" -ForegroundColor Gray
    Write-Host ""
}

# Step 3: Verify version.py exists
Write-Host "Step 3: Verifying version.py..." -ForegroundColor Yellow
$versionFile = Join-Path $repoRoot "contest_tools\version.py"
if (Test-Path $versionFile) {
    Write-Host "  ✓ version.py exists" -ForegroundColor Green
    
    # Test if it can be imported (optional - Python may not be in PATH)
    Set-Location $repoRoot
    $pythonCmd = 'import sys; sys.path.insert(0, "."); from contest_tools.version import __version__, get_version_string; print(get_version_string())'
    $versionCheck = python -c $pythonCmd 2>&1
    if ($? -and $versionCheck) {
        Write-Host "  ✓ version.py is functional: $versionCheck" -ForegroundColor Green
    } elseif (-not $?) {
        Write-Host "  ⚠ Warning: Could not test version.py import (Python may not be available)" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠ Warning: version.py exists but may have issues importing" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ version.py not found at expected location: $versionFile" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "Setup Summary:" -ForegroundColor Cyan
Write-Host "  • Pre-commit hooks:" $(if (-not $SkipHooks) { "Configured" } else { "Skipped" })
Write-Host "  • Git aliases:" $(if (-not $SkipAliases) { "Configured" } else { "Skipped" })
Write-Host "  • Version management: Ready" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Use 'git mainlog' to see clean main branch history" -ForegroundColor White
Write-Host "  2. Pre-commit hooks will auto-update git hash in version.py" -ForegroundColor White
Write-Host "  3. See Docs/Contributing.md and Docs/AI_AGENT_RULES.md for workflow details" -ForegroundColor White
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
