@echo off
rem Stage 2: every combination of command line parameters.
rem Close each emulator window to start the next call.
cd /d "%~dp0.."

echo [1/4] no parameters
call run.bat

echo [2/4] --script only
call run.bat --script startup\stage2.txt

echo [3/4] --vfs only
call run.bat --vfs vfs\several.csv

echo [4/4] --vfs and --script
call run.bat --vfs vfs\several.csv --script startup\stage2.txt

echo Done.
