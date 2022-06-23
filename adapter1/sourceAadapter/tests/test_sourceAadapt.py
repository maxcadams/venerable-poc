"""
Test sourceA adapter logic.

Author: Max Adams

In test functions,
_wf suffix means wells fargo specific checks
"""


import pytest

from decimal import Decimal
import boto3

import sourceAadapter
import pprint 

# dyn_resource = boto3.resource('dynamodb')

example_data = {
   "id": "5b288c57-bb42-4e38-b42c-afbe13816dab",
   "SourceId": "GARWIN",
   "CycleDate": "20220315",
   "BatchDate": "20220314",
   "BatchId": 123591,
   "BatchSeq": 1,
   "Site": "WC",
   "TransType": "CHK",
   "TransactionCd": "DTH",
   "ContractNum": "15681-61-2062",
   "Amount": "$15,231.36",
   "ClaimNum": 320695,
   "CompanyId": "VIAC",
   "CostCenter": 10062,
   "AnnuitantName": "",
   "AnnuitantStreet": "",
   "AnnuitantCity": "",
   "AnnuitantState": "",
   "AnnuitantZipcode": None,
   "BeneficiaryName": "Bill Suthington",
   "BeneficiaryStreet": "72 Walnut Street",
   "BeneficiaryCity": "West Deptford",
   "BeneficiaryState": "NJ",
   "BeneficiaryZipcode": 8096,
   "OtherPayeeName": "",
   "OtherPayeeStreet": "",
   "OtherPayeeCity": "",
   "OtherPayeeState": "",
   "OtherPayeeZipcode": None,
   "SpeedChart": 22,
   "Message": "Death Interest details for this disbursement are shown below",
   "IssuerBankName": "Wells Fargo",
   "IssuerBankABA": 21200025,
   "IssuerBankAccount": "WFPMTS"
  }

#PaymentInstructionList
pil = []
sourceAadapter.build_PaymentInstruction(example_data, pil)

def test_outer_node():
    """
    Checks if 'PaymentInstruction' node exists
    """
    assert 'PaymentInstruction' in pil[0].keys() 

pi = pil[0]['PaymentInstruction'] # get the single payment instruction from pi list


def test_payment_instruction_nodes_wf():
    """
    This tests the PaymentInstruction build for a single entry.
    Checks if fields needed for Wells Fargo file are created.
    """

    # checks if outer keys are there
    pi_keys = pi.keys()
    assert 'PayeeDetails' in pi_keys
    assert 'PaymentInfo' in pi_keys
    assert 'ContextSource' in pi_keys 

def test_PayeeDetails_wf():
    """
    Checks for valid PayeeDetail nodes and for 
    nodes within PayeeDetails
    """
    #checks PayeeDetails keys
    PayeeDetailsKeys = pi['PayeeDetails'].keys()
    assert 'AnnuityPolicyId' in PayeeDetailsKeys
    assert 'PayeeParty' in PayeeDetailsKeys
    assert 'PaymentAnnotation' in PayeeDetailsKeys

    #checks PayeeDetails.PayeeParty keys
    PayeePartyKeys = pi['PayeeDetails']['PayeeParty'].keys()
    assert 'FullName' in PayeePartyKeys
    assert 'Address' in PayeePartyKeys

    #checks PayeeDetails.PayeeParty.Address keys
    AddressKeys = pi['PayeeDetails']['PayeeParty']['Address'].keys()
    assert 'Street' in AddressKeys
    assert 'City' in AddressKeys
    assert 'State' in AddressKeys
    assert 'Zip' in AddressKeys

def test_PaymentInfo_wf():
    """
    Checks for valid PaymentInfo nodes and for
    nodes within PaymentInfo nodes. 
    """
    #checks PaymentInfo keys
    PaymentInfoKeys = pi['PaymentInfo'].keys()
    assert 'Payment' in PaymentInfoKeys

    #checks Payment keys
    PaymentKeys = pi['PaymentInfo']['Payment']
    assert 'CurrencyAmount' in PaymentKeys
    assert 'CurrencyInstrument' in PaymentKeys

    #checks Payment.CurrencyInstrument.Symbol existence
    CIKeys = pi['PaymentInfo']['Payment']['CurrencyInstrument']
    assert 'Symbol' in CIKeys

def test_ContextSource_wf():
    """
    Checks for valid ContextSources nodes.
    """
    #checks ContextSource.Source existence
    CSKeys = pi['ContextSource']
    assert 'Source' in CSKeys
