@echo off
rem Stage 4: startup script with ls, cd, cat, tail and history.
rem Close the emulator window to finish.
cd /d "%~dp0.."

echo [1/1] stage 4 commands on deep VFS
call run.bat --vfs vfs\deep.csv --script startup\stage4.txt

echo Done.
