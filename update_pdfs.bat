@echo off
setlocal enabledelayedexpansion

echo --- Starting PDF Conversion for Documentation ---

REM --- Process README.md in the root directory ---
call :ConvertIfNeeded "README.md" "README.pdf"

REM --- Process all .md files in the Docs directory ---
set "DOC_DIR=Docs"
if not exist "%DOC_DIR%" (
    echo Error: The '%DOC_DIR%' directory was not found.
    goto :eof
)

for %%F in ("%DOC_DIR%\*.md") do (
    call :ConvertIfNeeded "%%F" "%%~dpnF.pdf"
)

echo.
echo --- PDF Conversion Complete ---
goto :eof

:: ============================================================================
:: Subroutine to perform the conversion only if the source is newer
:: %1 - Input Markdown file path
:: %2 - Output PDF file path
:: ============================================================================
:ConvertIfNeeded
set "MD_FILE=%~1"
set "PDF_FILE=%~2"

if not exist "%MD_FILE%" (
    echo Warning: Source file not found: "%MD_FILE%". Skipping.
    goto :eof
)

echo Processing: "%MD_FILE%"

if not exist "%PDF_FILE%" (
    echo  -> PDF does not exist. Generating...
    pandoc -f gfm "%MD_FILE%" --pdf-engine=xelatex -o "%PDF_FILE%"
) else (
    for %%M in ("%MD_FILE%") do set "MD_TIME=%%~tM"
    for %%P in ("%PDF_FILE%") do set "PDF_TIME=%%~tP"

    if "!MD_TIME!" GTR "!PDF_TIME!" (
        echo  -> Markdown file is newer. Regenerating PDF...
        pandoc -f gfm "%MD_FILE%" --pdf-engine=xelatex -o "%PDF_FILE%"
    ) else (
        echo  -> PDF is up-to-date. Skipping.
    )
)
goto :eof