@echo off
rem Stage 3: VFS loading errors are shown in the window.
rem Close each emulator window to start the next call.
cd /d "%~dp0.."

echo [1/2] VFS file does not exist
call run.bat --vfs vfs\no_such_vfs.csv --script startup\stage3.txt

echo [2/2] VFS file with invalid base64 data
call run.bat --vfs vfs\broken.csv --script startup\stage3.txt

echo Done.
