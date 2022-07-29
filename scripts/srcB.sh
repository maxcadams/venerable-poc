#!/bin/sh

cd src/producers/sourceB;
echo 'exit' | python3 sourceBdb.py
cd ../../..
./scripts/exec.sh;
cd src/producers/sourceB;
python3 sourceBdb.py