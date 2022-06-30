

import json
from decimal import Decimal
import csv
import uuid
from venv import create
import urllib3
from datetime import datetime, date
import random
import logging
import boto3
from botocore.exceptions import ClientError
import os

logger = logging.getLogger(__name__)

orch_url = 'https://bdt2raiww8.execute-api.us-east-1.amazonaws.com/dev/orch'

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

def create_bucket(s3, bucket_name):
    """
    
    """
    # s3 = boto3.resource('s3')

    s3.create_bucket(Bucket=bucket_name)

    return s3.Bucket(bucket_name)

def delete_bucket(s3, bucket):
    """
    
    """
    for item in bucket.objects.all():
       s3.Object(bucket.name, item.key).delete() 
    bucket.delete()


def main():
    file_name = ''
    with create_file() as file:
        add_data(get_orch_data(orch_url), file)
        file_name = file.name
    
    #creates new dir and moves file into it
    new_dir = r'wf_files'
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, new_dir)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    os.replace(f"{current_directory}/{file_name}", f"{final_directory}/{file_name}")

    #creates s3 nicket
    s3 = boto3.resource('s3')
    bucket_name = 'wf-consumer-bucket-' + str(uuid.uuid4())
    bucket = create_bucket(s3, bucket_name)
    bucket.upload_file(f'{new_dir}/{file_name}', f'{file_name}')

    while(True):
        prompt = input("Type 'finish' to delete bucket and end process: ")
        if (prompt == 'finish'):
            break
    delete_bucket(s3, bucket)
    print('Bucket deleted')
    
if __name__ == '__main__': 
    main()
    


