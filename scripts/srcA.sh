#!/bin/sh
cd src/producers/sourceA;
echo 'exit' | python3 sourceAdb.py 
cd ../..;
while [ ! -s adapters/sourceAadapter/table_arn.txt ]
do 
  sleep 1
done
cd ..
./scripts/exec.sh;
cd src/producers/sourceA;
python3 sourceAdb.py