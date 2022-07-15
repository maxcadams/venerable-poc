#!/bin/zsh

execute () {
    sls deploy | tee deploy_logs.txt;
    cat deploy_logs.txt | grep "endpoint:" | xargs >> ../api_endpoint.txt;
}

cd ../src;
# go to sourceAadapter and deploy
cd sourceAadapter;
execute
cd ../sourceBadapter;
execute
cd ../orch;
cat ../api_endpoint.txt > adapter_urls.txt
execute
cat deploy_logs.txt | grep "endpoint:" | xargs > ../wf_consumer/orch_url.txt;
cd ..
