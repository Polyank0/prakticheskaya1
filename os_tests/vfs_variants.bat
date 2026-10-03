@echo off
rem Stage 3: emulator with different VFS files.
rem Close each emulator window to start the next call.
cd /d "%~dp0.."

echo [1/3] minimal VFS: one file
call run.bat --vfs vfs\minimal.csv --script startup\stage3.txt

echo [2/3] VFS with several files
call run.bat --vfs vfs\several.csv --script startup\stage3.txt

echo [3/3] VFS with three levels of folders
call run.bat --vfs vfs\deep.csv --script startup\stage3.txt

echo Done.
