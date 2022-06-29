import pytest
import csv
from datetime import date, datetime
import json

from wf_consumer import add_data, create_file

def test_headers():
    with open('output.json') as file_in:
        body = json.load(file_in)
        transactions = body['Transactions']['PaymentInstructions']
        with create_file() as file: # use with as here because create_file opens fd
            add_data(transactions=transactions, file=file)
            file.seek(0)
            reader = csv.reader(file)
            #headers = reader.__next__() #gives us headers in a list
            ref_headers = ['BatchID', 'SequenceID', 
                            'BatchDate', 'PolicyNum', 
                            'PayeeFullName', 'PayeeStreet', 
                            'PayeeCity', 'PayeeState', 
                            'PayeeZipcode', 'Account', 
                            'Comments', 'Amount', 
                            'Currency', 'SourceSystem']
            headers = reader.__next__()
            for header in headers:
                assert header in ref_headers
                

        