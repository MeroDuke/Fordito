@echo off
REM =========================================
REM Release branch merge script - Template
REM Supports custom branch suffix (e.g. testing, preOCR, ci-ready)
REM =========================================

REM === CONFIGURATION ===
set VERSION=1.4.2
set BRANCH_SUFFIX=ASS-layout-refactor

REM === Checkout main branch and pull latest changes ===
git checkout main
git pull

REM === Merge release branch into main ===
git merge release-%VERSION%-%BRANCH_SUFFIX% --no-ff -m "Release %VERSION%"

REM === Tag the release on main ===
git tag -a v%VERSION% -m "Version %VERSION%"
git push origin v%VERSION%

REM === Push changes to main ===
git push

REM === Optional: Clean up release branch ===
REM Branch deletion is intentionally disabled to allow later hotfixes or history review.
REM Uncomment the lines below only if you want to delete the release branch after merge.
REM git branch -d release-%VERSION%-%BRANCH_SUFFIX%
REM git push origin --delete release-%VERSION%-%BRANCH_SUFFIX%

echo Release process for %VERSION% with suffix '%BRANCH_SUFFIX%' completed.
pause