@echo off
REM Change these paths before running
set FILE_PATH=<replace with path to your zip file>
set num_of_docs=100
set k=10
set SIGLEN=128
set THRESH=0.8

python main.py --zipfile "%FILE_PATH%" --num-of-docs %num_of_docs% --shingle-length %k% --signature-length %SIGLEN% --threshold %THRESH%
pause
