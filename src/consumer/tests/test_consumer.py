import csv
import json
import os

import pytest
from consumer import add_data, create_file


def test_headers():
    with open("output.json") as file_in:
        body = json.load(file_in)
        transactions = body["Transactions"]["PaymentInstructions"]
        with create_file() as file:  # use with as here because create_file opens fd
            add_data(transactions=transactions, file=file)
            file.seek(0)
            reader = csv.reader(file)
            ref_headers = [
                "BatchID",
                "SequenceID",
                "BatchDate",
                "PolicyNum",
                "PayeeFullName",
                "PayeeStreet",
                "PayeeCity",
                "PayeeState",
                "PayeeZipcode",
                "Account",
                "Comments",
                "Amount",
                "Currency",
                "SourceSystem",
            ]
            headers = next(reader)
            for header in headers:
                assert header in ref_headers
        os.remove(file.name)
