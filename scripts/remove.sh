#!/bin/sh

cd src/adapters/sourceAadapter;
sls remove;
: > deploy_logs.txt
: > table_arn.txt

cd ../sourceBadapter;
: > deploy_logs.txt
sls remove;
: > bucket_name.txt
: > deploy_logs.txt

cd ../../orch;
sls remove;
: > adapter_urls.txt
: > deploy_logs.txt

cd ../consumer;
: > orch_url.txt
rm -rf sheets;
