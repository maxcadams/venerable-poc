import json
import os
from unicodedata import decimal
import decimalencoder
import boto3


dynamodb = boto3.resource('dynamodb')

def adapt(event, context):
    
    table1 = dynamodb.Table(os.environ['TRANSACTIONS_TABLE'])
    table2 = dynamodb.Table(os.environ['MATCHES_TABLE'])

    transactions_scan = table1.scan()
    matches_scan = table2.scan()


    transactions = transactions_scan['Items']
    matches = matches_scan['Items']

    response = {
        "statusCode": 200,
        "body": f"""{{
            "transactions":{json.dumps(transactions, cls=decimalencoder.DecimalEncoder)},
            "matches":{json.dumps(matches, cls=decimalencoder.DecimalEncoder)}
            }}"""
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
