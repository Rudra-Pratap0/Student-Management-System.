@echo off
title Student Management System - Launcher
cd /d "%~dp0"
echo ===================================================
echo   STUDENT MANAGEMENT SYSTEM - LAUNCHER
echo   Python, Tkinter, SQLite3
echo ===================================================
echo.
echo Launching application...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application failed to launch or exited unexpectedly.
    echo Please make sure Python 3 is installed and added to your PATH.
    echo.
    pause
)
