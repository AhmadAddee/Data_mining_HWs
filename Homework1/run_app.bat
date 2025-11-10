@echo off
REM Change these paths before running
set FILE_PATH=<replace with path to your zip file>
set num_of_docs=100
set SIGLEN=256
set k=10
set THRESH=0.8

python main.py --zipfile "%FILE_PATH%" --num-of-docs %num_of_docs% --benchmark --grid-k %k% --grid-siglen %SIGLEN% --grid-threshold %THRESH% --grid-bands auto --sizes 5,10,20,40,80,160,320,740,1000 --repeat 1 --plot-out runtime.png
pause
