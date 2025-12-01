@echo off
REM Change these paths before running
set DIR_PATH=<replace with path to the dir where graph-files are located>
set communities=10

python main.py --data-dir "%DIR_PATH%" -k %communities% --plot
pause
