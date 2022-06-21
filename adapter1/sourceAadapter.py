import json
import decimalencoder
import os
import boto3
from decimal import Decimal


"""
Lambda handler that takes in data from sourceA and adapts it to domain model
schema. 

Right now, we should form all of the look up files, 
then start building from the inside and move out.

BE AS LAZY AS POSSIBLE (when coding)
-- with lookups, try to make it a single function

-- break down building model structure into several no-input functions

-- 
"""








def adapt(event, context):
    
    response = {
        "statusCode": 200,
        "body": json.dumps()
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
