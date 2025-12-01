#!/usr/bin/env bash
# Change these paths before running
FILE_PATH=<"replace with path to your graph-file">
communities=10

python main.py --data-file "$FILE_PATH" -k communities --plot
