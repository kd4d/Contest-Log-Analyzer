@echo off
setlocal enabledelayedexpansion
echo --- Starting PDF Conversion for Documentation ---

REM --- Process README.md in the root directory ---
set README_FILE=README.md
if exist "%README_FILE%" (
    echo Processing: "%README_FILE%"
    set PDF_OUT="README.pdf"
    REM Use delayed expansion (!PDF_OUT!) here as well.
    pandoc -f gfm "%README_FILE%" --pdf-engine=xelatex -o !PDF_OUT!
) else (
    echo Warning: README.md not found in the project root.
)

REM --- Process all .md files in the Docs directory ---
set DOC_DIR=Docs
if not exist "%DOC_DIR%" (
    echo Error: The '%DOC_DIR%' directory was not found.
    goto :eof
)

for %%F in ("%DOC_DIR%\*.md") do (
    echo Processing: "%%~nxF"
    set PDF_OUT="%%~dpnF.pdf"
    pandoc -f gfm "%%F" --pdf-engine=xelatex -o !PDF_OUT!
)

echo.
echo --- PDF Conversion Complete ---