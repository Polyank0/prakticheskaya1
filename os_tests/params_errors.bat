@echo off
rem Stage 2: wrong values of command line parameters.
rem Close each emulator window to start the next call.
cd /d "%~dp0.."

echo [1/3] startup script does not exist
call run.bat --script startup\no_such_script.txt

echo [2/3] unknown parameter: usage text is printed here
call run.bat --color red

echo [3/3] parameter without value: usage text is printed here
call run.bat --script

echo Done.
