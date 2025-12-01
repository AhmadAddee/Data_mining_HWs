#!/usr/bin/env bash
# Change these paths before running
DIR_PATH=<"replace with path to the dir where graph-files are located">
communities=10

python main.py --data-dir "$DIR_PATH" -k communities --plot
