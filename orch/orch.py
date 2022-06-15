from email.quoprimime import body_check
import json
import urllib3
import decimalencoder

url = 'https://7pl2f71oh7.execute-api.us-east-1.amazonaws.com/dev/all'

def orch(event, context):

    http = urllib3.PoolManager()
    res = http.request('GET', url)


    body = res.data.decode('utf-8')

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Credentials': True
        },
        "body": body
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
