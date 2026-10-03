@echo off
rem Stages 4 and 5: startup scripts with all commands.
rem Close each emulator window to start the next call.
cd /d "%~dp0.."

echo [1/2] stage 4: ls, cd, cat, tail, history on deep VFS
call run.bat --vfs vfs\deep.csv --script startup\stage4.txt

echo [2/2] stage 5: cp on VFS with several files
call run.bat --vfs vfs\several.csv --script startup\stage5.txt

echo Done.
