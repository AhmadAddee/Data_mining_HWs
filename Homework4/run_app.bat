@echo off
REM Change these paths before running
set FILE_PATH=<replace with path to your graph-file>
set communities=10

python main.py --data-file "%FILE_PATH%" -k %communities% --plot
pause
