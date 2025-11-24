@echo off
REM Change these paths before running
set FILE_PATH=C:\Skolan\TSEDM1\Data mining ID2222\Data_mining_HWs\Homework3\dataset\web-NotreDame.txt.gz
set memories=15000 150000 300000 450000 600000 750000 1000000

python main.py --data-file "%FILE_PATH%" --memory %memories% --plot
pause
