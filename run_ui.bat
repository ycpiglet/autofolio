@echo off
REM Retired Streamlit launcher. Start the FastAPI backend and Next.js frontend.
start "Autofolio API" cmd /k "%~dp0run_api.bat"
start "Autofolio Web" cmd /k "%~dp0run_frontend.bat"
