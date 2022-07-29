#!/bin/sh

execute () {
    sls deploy --verbose| tee deploy_logs.txt;
}

cd src/adapters;

if [ ! -s ../orch/adapter_urls.txt ]
then
  # if adapter_urls.txt empty, deploy sourceAadapter
  cd sourceAadapter;
  execute
  cat deploy_logs.txt | grep "endpoint:" | xargs > ../../orch/adapter_urls.txt;
else
  # else (meaning sourceA already standing and url already in file) 
  # deploy sourceBadapter and add endpoint url to file
  cd sourceBadapter;
  execute
  cat deploy_logs.txt | grep "endpoint:" | xargs >> ../../orch/adapter_urls.txt
fi
cd ../../orch;
# deploy orch
execute
cat deploy_logs.txt | grep "endpoint:" | xargs > ../consumer/orch_url.txt;
