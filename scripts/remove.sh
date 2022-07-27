#!/bin/zsh

cd src/adapters/sourceAadapter;
sls remove;
: > table_arn.txt
cd ../sourceBadapter;
sls remove;
: > bucket_name.txt
cd ../../orch;
sls remove;
: > adapter_urls.txt
cd ../consumer;
rm -rf sheets;
