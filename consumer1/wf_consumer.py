

import json
from decimal import Decimal
import csv
from urllib import response
import urllib3
import uuid
from datetime import date
import random

orch_url = 'https://v2mmu22kh0.execute-api.us-east-1.amazonaws.com/dev/orch'

def get_orch_data(url):
    """
    Gets data from orchestrator.
    :param url: API endpoint for orchestrator.
    :return: Response body as dict.
    """
    #PoolManager manges connection
    http = urllib3.PoolManager()
    
    HTTPres = http.request('GET', url)
    #convert to stirng
    response = HTTPres.data.decode('utf-8')
    body = json.loads(response)

    return body

def create_file():
    """
    Creates csv file for batch data
    :return: file descriptor for file we ar creating
    """
    today = date.today()

    today_str = today.strftime("%Y.%m.%d.%H.%M.%S")
    file_name = today_str + '.WellsFargo.Payments.csv'

    return open(file_name, 'w', encoding='UTF8', newline='')

def add_data():
    field_names = ['BatchID', 'SequenceID', 'BatchDate', 'PolicyNum', 
        'PayeeFullName', 'PayeeStreet', 'PayeeCity', 'PayeeState', 'PayeeZipcode',
        'Account', 'Comments', 'Amount', 'Currency', 'SourceSystem']

    
    



if __name__ == '__main__':
    body = get_orch_data(orch_url)