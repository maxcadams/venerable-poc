#!/bin/zsh

: > api_endpoint.txt
# go to sourceAadapter and deploy
cd sourceAadapter;
sls remove;
cd ../sourceBadapter;
sls remove;
cd ../orch;
sls remove;
cd ..;