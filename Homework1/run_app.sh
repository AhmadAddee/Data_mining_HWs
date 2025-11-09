#!/usr/bin/env bash
# Change these paths before running
FILE_PATH=<"replace with path to your zip file">
num_of_docs=10
k=10
SIGLEN=128
THRESH=0.8

python main.py --zipfile "$FILE_PATH" --num-of-docs $num_of_docs -k $k -n $SIGLEN -t $THRESH
