#!/usr/bin/env bash
# Change these paths before running
FILE_PATH=<"replace with path to your data file">
set SUPPORT=1000
set CONFIDENCE=0.5

python main.py --data-file "$FILE_PATH" --support-threshold $SUPPORT --confidence-threshold $CONFIDENCE
