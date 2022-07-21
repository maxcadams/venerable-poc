#!/bin/zsh

cd src/adapters/sourceAadapter;
sls remove;
cd ../sourceBadapter;
sls remove;
cd ../../orch;
sls remove;
: > adapter_urls.txt