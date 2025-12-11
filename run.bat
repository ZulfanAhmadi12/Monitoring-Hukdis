@echo off
chcp 65001 >nul
title Hukdis Monitoring System Launcher

echo ==============================================
echo   Hukdis Monitoring System - Launcher
echo ==============================================

set BASE=%~dp0
set PYTHON=%BASE%python_embedded\python.exe
set SCRIPTS=%BASE%python_embedded\Scripts

if not exist "%PYTHON%" (
    echo [ERROR] python_embedded\python.exe not found!
    pause
    exit /b
)

if not exist "%SCRIPTS%" (
    echo [ERROR] python_embedded\Scripts not found!
    pause
    exit /b
)

set UVICORN=%SCRIPTS%\uvicorn.exe
set STREAMLIT=%SCRIPTS%\streamlit.exe

if not exist "%UVICORN%" (
    echo [ERROR] uvicorn.exe not found in python_embedded\Scripts
    pause
    exit /b
)

if not exist "%STREAMLIT%" (
    echo [ERROR] streamlit.exe not found in python_embedded\Scripts
    pause
    exit /b
)

rem ----------------------------------------------------
rem 1. Start Backend (FastAPI)
rem ----------------------------------------------------

echo Starting Backend (FastAPI + Uvicorn)...
start "" "%UVICORN%" backend.app.main:app --host 0.0.0.0 --port 8000

echo Waiting backend to boot...
timeout /t 3 >nul

rem ----------------------------------------------------
rem 2. Detect WiFi IP
rem ----------------------------------------------------
echo Detecting IPv4...

for /f "usebackq tokens=* delims=" %%i in (`powershell -NoProfile -Command ^
    "(Get-NetIPAddress | Where-Object { $_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' })[0].IPAddress"`) do (
    set WIFI_IP=%%i
)

if "%WIFI_IP%"=="" (
    echo [WARNING] No active IPv4 found. Using localhost.
    set WIFI_IP=127.0.0.1
)

echo [INFO] Using IP Address: %WIFI_IP%


rem ----------------------------------------------------
rem 3. Start Frontend (Streamlit)
rem ----------------------------------------------------

echo Starting Frontend (Streamlit)...
start "" "%STREAMLIT%" run "frontend/main.py" --server.address %WIFI_IP% --server.port 8501 --server.headless true

echo.
echo ==============================================
echo   Hukdis Monitoring System Running
echo ==============================================
echo Backend  : http://%WIFI_IP%:8000
echo Frontend : http://%WIFI_IP%:8501
echo ==============================================

pause
exit /b
