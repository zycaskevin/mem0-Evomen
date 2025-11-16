@echo off
setlocal enabledelayedexpansion

set REVIEW_TYPE=%1
if "%REVIEW_TYPE%"=="" (
    set REVIEW_TYPE=code
) else (
    shift
)

set REVIEW_INPUT=%1
if "%REVIEW_INPUT%"=="" (
    if /I "%REVIEW_TYPE%"=="plan" (
        set REVIEW_INPUT=docs\plan.md
    ) else (
        set REVIEW_INPUT=src
    )
) else (
    shift
)

set REVIEW_OUTPUT=%1
if "%REVIEW_OUTPUT%"=="" (
    set REVIEW_OUTPUT=data\reviews
) else (
    shift
)

set EXTRA_ARGS=%*

python "%~dp0scripts\review_runner.py" ^
    --type=%REVIEW_TYPE% ^
    --input="%REVIEW_INPUT%" ^
    --output="%REVIEW_OUTPUT%" ^
    --models codex gemini %EXTRA_ARGS%

endlocal
