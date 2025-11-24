#!/usr/bin/env bash
# Change these paths before running
FILE_PATH=<"replace with path to your zip file">
memories=15000 150000 300000 450000 600000 750000 1000000

python main.py --data-file "$FILE_PATH" --memory memories --plot
