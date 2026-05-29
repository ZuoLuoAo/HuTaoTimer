@echo off
setlocal enabledelayedexpansion

REM 过滤 PATH 中的 Anaconda/Msys/Cygwin 路径
set "CLEAN_PATH="
for %%p in ("%PATH:;=" "%") do (
    set "p=%%~p"
    echo !p! | findstr /i "Anaconde Anaconda mingw msys cygwin" >nul
    if errorlevel 1 (
        if defined CLEAN_PATH (
            set "CLEAN_PATH=!CLEAN_PATH!;!p!"
        ) else (
            set "CLEAN_PATH=!p!"
        )
    )
)
set "PATH=%CLEAN_PATH%"

.venv\Scripts\python.exe pomodoro\main.py
