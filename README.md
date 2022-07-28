# Adapter Integration POC
For Venerable, Summer 2022.

Adapter Integration POC demonstrating the simplicity and benefits of a Hub-and-Spoke model.

## Setup
Make sure you have Serverless Framework setup with AWS.
This [link](https://www.serverless.com/framework/docs/getting-started) contains instructions of setting up
Serverless with your AWS account.

Running the scripts below configures the serverless.yml files to match with the corresponding database ARNs.

## Running POC
**Make sure you run the POC in the order stated, or else it will not work. If anything disrupts
   the deployment of any of the pieces, run the remove script and start over.**

1. Standup sourceA and sourceAadapter. 
```
./scripts/srcA.sh
```
This scripts does the following:
* Gets the arn of the DynamoDb and puts it into a src/adapters/sourceAadapter/table_arn.txt so that the serverless.yml can config correctly.
* Then once arn is in the file above, it deploys the REST API using Serverless framework and AWS API Gateway and Lambda. The endpoint for sourceAadapter is pulled from the deploy logs and is put into src/orch/adapter_urls.txt 
* Then runs the prompt for the DynamoDB sourceA. 

After this, you can go to step 3 run the consumer script with just sourceA data.

2. Standup sourceB and sourceBadapter. Do this in a different terminal window than sourceA. * Run this only after srcA has been ran.**
```
./scripts/srcB.sh
```
* Gets the name of the s3 bucket created for sourceB and puts it into a src/adapters/sourceBadapter/bucket_name.txt
     so that the serverless.yml can config correctly.
    Note: We do this because all buckets must be uniquely named across AWS.
* Then once the bucket name is in the file above, it deploys the REST API using Serverless framework
     and AWS API Gateway and Lambda. The endpoint for sourceBadapter is pulled from the deploy logs and is put into src/orch/adapter_urls.txt. The orch endpoint url is put into src/consumer/orch_url.txt for the convumer to use.
* Then runs the prompt for sourceB s3 bucket. 

3. Consumer side script. Run this in a third terminal window.
```
./scripts/consumer_exec.sh
```
This calls the orchestrator (middleman) api, pulls the data and formats it in a csv file
that is named YYYY.MM.DD.HH.MM.Bank.Payments.csv. The csv file is then uploaded to an s3 bucket, which can be torn
down in the prompt, and the file is also locally moved to src/consumer/sheets .


## Clean Up

1. From the venerable-poc run the script below.
```
./scripts/remove.sh

This script takes down the APIs and clears all of the files that store any url, or resource name.

```
2. Make sure that for both the sourceA and sourceB prompts, make sure you have input 'finish' to both prompts. If you exited one of them without
deleting the resources, you'll have to run the individual scripts in src/producer/source_ and input finish when you run
```
python3 source_db.py
```
