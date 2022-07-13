import urllib3
import json
import sys
sys.path.append('..')
from helper_package import decimalencoder

with open('adapter_urls.txt') as file:
    urls = [line[line.index('h'):].rstrip('\n') for line in file.readlines()]

def build_domain(pi_list):
    domain = { "Transactions": {
                "SchemaVersion": "v1.0",
                "PaymentInstructions": pi_list
        }
    }
    return domain

def get_PaymentInstructions(url, http):
    res = http.request('GET', url)
    body_str = res.data.decode('utf-8')
    body_dict = json.loads(body_str)
    return body_dict['Transactions']['PaymentInstructions']

def orch(event, context):
    """
    Lambda function that gets called when orch is needed.
    """
    http = urllib3.PoolManager()
    pi_list_of_lists = [get_PaymentInstructions(url, http) for url in urls]
    flattened_pi = [pi for sublist in pi_list_of_lists for pi in sublist]
    domain = build_domain(flattened_pi)


    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Credentials': True
        },
        "body": json.dumps(domain, cls=decimalencoder.DecimalEncoder)
    }

    return response