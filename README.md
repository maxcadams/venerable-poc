# Adapter Integration POC
For Venerable, Summer 2022.

Adapter Integration POC demonstrating the simplicity and benefits of a Hub-and-Spoke model.

## Setup
Make sure you have Serverless Framework setup with AWS.
This [link](https://www.serverless.com/framework/docs/getting-started) contains instructions of setting up
Serverless with your AWS account.
rm 
## Running POC
**Make sure you run the POC in the order stated, or else it will not work. If anything disrupts
   the deployment of any of the pieces, run the remove script and start over.**

1. Standup sourceA and sourceAadapter. 
```
./scripts/srcA.sh
```
After this, you can go to step 3 run the consumer script with just sourceA data.

2. Standup sourceB and sourceBadapter. * Run this only after srcA has been ran.**
```
./scripts/srcB.sh
```

3. Consumer side script. 
```
./scripts/consumer_exec.sh
```
This calls the orchestrator (middleman) api, pulls the data and formats it in a csv file
that is named YYYY.MM.DD.HH.MM.Bank.Payments.csv. The csv file is then uploaded to an s3 bucket, which can be torn
down in the prompt, and the file is also locally moved to src/consumer/sheets .