#!/bin/sh

cd src/adapters/sourceAadapter;
python3 -m pytest;
cd ../sourceBadapter;
python3 -m pytest;
cd ../../consumer;
python3 -m pytest;
