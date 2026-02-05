@echo off
echo.
echo ============================================
echo   NOTICE: setup_venv.bat is deprecated
echo ============================================
echo.
echo   The new install.bat handles everything automatically,
echo   including downloading Python and Git portably.
echo.
echo   No system Python or Git installation required.
echo.
echo   Launching install.bat...
echo.
call "%~dp0install.bat" %*
