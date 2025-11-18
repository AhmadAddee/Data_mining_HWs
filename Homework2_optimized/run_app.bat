@echo off
REM Change these paths before running
set FILE_PATH=C:\Skolan\TSEDM1\Data mining ID2222\Data_mining_HWs\Homework2\dataset\T10I4D100K.dat
set SUPPORT=1000
set CONFIDENCE=0.5

python main.py --data-file "%FILE_PATH%" --support-threshold %SUPPORT% --confidence-threshold %CONFIDENCE%
pause
