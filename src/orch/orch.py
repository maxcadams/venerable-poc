"""
For Venerable POC, Summer 2022.

Orchestrator lambda handler that calls adapter endpoints and aggregates
data to domain model.

Author: Max Adams
"""

import json
import sys

import urllib3

sys.path.append("..")
from helper_package import decimalencoder

# pulls endpoints from adapter_urls.txt, a file that contains adapter endpoints
with open("adapter_urls.txt") as file:
    urls = [line[line.index("h"):].rstrip("\n") for line in file]


def build_domain(pi_list):
    """
    Builds domain model.

    :param pi_list: PaymentInstructions list of aggregated data from each
                    endpoint.
    :return: Domain Model with aggregated data.
    """
    domain = {"Transactions": {"SchemaVersion": "v1.0", "PaymentInstructions": pi_list}}

    return domain


def get_PaymentInstructions(url, http):
    """
    Gets payment instruction from input url. (Adapter endpoint)

    :param url: Endpoint for adapter api.
    :param http: PoolManager from urllib3 that keeps track of connection
                 and requests being made.
    """
    res = http.request("GET", url)
    body_str = res.data.decode("utf-8")
    body_dict = json.loads(body_str)

    return body_dict["Transactions"]["PaymentInstructions"]


def orch(event, context):
    """
    Lambda function that gets called when orch is needed.
    """
    http = urllib3.PoolManager()

    # List of PaymentInstructions from each source.
    pi_list_of_lists = [get_PaymentInstructions(url, http) for url in urls]

    # Flattens list of PaymentInstructions (essentially aggregates everything)
    flattened_pi = [pi for sublist in pi_list_of_lists for pi in sublist]

    domain = build_domain(flattened_pi)

    response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": True},
        "body": json.dumps(domain, cls=decimalencoder.DecimalEncoder),
    }

    return response
