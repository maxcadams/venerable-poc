

import json
from decimal import Decimal
import csv
from venv import create
import urllib3
import uuid #necessary if we change batchId method
from datetime import datetime, date
import random

orch_url = 'https://5q0whtjg5d.execute-api.us-east-1.amazonaws.com/dev/orch'


def lookup(alias, alias_set, lookup_file):
    """
    Performs a party look up by alias in alias_set.

    :param alias: Alias of party we are looking up.
    :param alias_set: Alias set in which party resides.
    :param lookup_file: File name of json (look up db)
    :return: Party information
    """
    with open(lookup_file) as file:
        file_content = json.load(file, parse_float=Decimal)

        if (lookup_file == 'Instrument.json'):
            return file_content
        elif(lookup_file == 'PersonParty.json'):
            person = list(filter(lambda payee: payee['FullName'] == alias, 
                        file_content[alias_set]))[0] 
                        # list(filter) returns list of one entry for person 
                        # with name 'alias', so we access elt @ index 0 
            return person
        
        #here, we are either in Account, BankParty, or OrganizationParty lookup
        return file_content[alias_set][alias]

def get_orch_data(url):
    """
    Gets data from orchestrator.

    :param url: API endpoint for orchestrator.
    :return: Response body as dict. Returns the PaymentInstructions list.
    """
    #PoolManager manges connection
    http = urllib3.PoolManager()
    
    HTTPres = http.request('GET', url)
    #convert to stirng
    response = HTTPres.data.decode('utf-8')
    body = json.loads(response)

    return body ['Transactions']['PaymentInstructions']

def create_file():
    """
    Creates csv file for batch data

    :return: file descriptor for file we ar creating
    """
    now = datetime.now()

    now_str = now.strftime("%Y.%m.%d.%H.%M.%S")
    file_name = now_str + '.WellsFargo.Payments.csv'

    return open(file_name, 'w+', encoding='UTF8', newline='')

#see if you can seperate create_file out of this function or redefine this function
def add_data(transactions, file):
    """
    Creates file and add data from transactions to csv file in one batch
    in Wells Fargo format. 

    :param transactions: Input transactions being put into csv file.
    :param file: File descriptor for file that we are adding data to.
                 (Should be .csv)
    """
    field_names = ['BatchID', 'SequenceID', 'BatchDate', 'PolicyNum', 
        'PayeeFullName', 'PayeeStreet', 'PayeeCity', 'PayeeState', 'PayeeZipcode',
        'Account', 'Comments', 'Amount', 'Currency', 'SourceSystem']

    # with create_file() as file:
    writer = csv.writer(file)
    
    # write headers in
    writer.writerow(field_names)
    sequenceIdCounter = 1
    batchId = random.randint(1,9999)
    for transaction in transactions:
        pi = transaction['PaymentInstruction']
        row = [ batchId, #BatchID .... do we want uuid or random num
                sequenceIdCounter, #SequenceID
                date.today().strftime('%Y%m%d'), #BatchDate
                pi['PayeeDetails']['AnnuityPolicyId'], #PolicyNum
                pi['PayeeDetails']['PayeeParty']['FullName'], #PayeeFullName 
                pi['PayeeDetails']['PayeeParty']['Address']['Street'], #PayeeStreet
                pi['PayeeDetails']['PayeeParty']['Address']['City'], #PayeeCity
                pi['PayeeDetails']['PayeeParty']['Address']['State'], #PayeeState
                pi['PayeeDetails']['PayeeParty']['Address']['Zip'], #PayeeZipcode
                lookup('VenerableCheckAccount', 'WellsFargoAccounts', 'Account.json'), #Account
                pi['PayeeDetails']['PaymentAnnotation'], #Comments
                pi['PaymentInfo']['Payment']['CurrencyAmount'], #Amount
                pi['PaymentInfo']['Payment']['CurrencyInstrument']['Symbol'], #Currency
                pi['ContextSource']['Source'], #SourceSystem
        ]
        writer.writerow(row)

        #increment sequence id
        sequenceIdCounter+=1

def main():
    add_data(get_orch_data(orch_url), create_file())

if __name__ == '__main__':
    
    main()
    
    # file_in = open('output.json')
    # body = json.load(file_in)
    # transactions = body['Transactions']['PaymentInstructions']
    # with create_file() as file:
    #     add_data(transactions, file)
    #     file.seek(0)
    #     reader = csv.reader(file)
    #     headers = reader.__next__()
    #     print(headers)


