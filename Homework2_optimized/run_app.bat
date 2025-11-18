@echo off
REM Change these paths before running
set FILE_PATH=<replace with path to your data file>
set SUPPORT=1000
set CONFIDENCE=0.5

python main.py --data-file "%FILE_PATH%" --support-threshold %SUPPORT% --confidence-threshold %CONFIDENCE%
pause
