@echo on
:: Change directories to the directory of this script
cd /d "%~dp0"
:: Option 1: Installed in, e.g.,  C:\Users\jbejarano\AppData\Local\anaconda3\
call "%USERPROFILE%\AppData\Local\anaconda3\Scripts\activate.bat" base
:: Option 2: Installed in, e.g., C:\Users\jbejarano\anaconda3
@REM call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base

echo Running in %CD%
echo Running "chartbase run-all-windows --skip-excel-refresh"
chartbase run-all-windows --skip-excel-refresh

pause

