"""
Test sourceA adapter logic. 
To test, we only check the keys, not the data.

Author: Max Adams
"""


import pytest
from sourceAadapter import build_PaymentInstruction

example_data = {
    "id": "5b288c57-bb42-4e38-b42c-afbe13816dab",
    "SourceId": "SOURCEA",
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
    "CompanyId": "COMP",
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
    "IssuerBankName": "BigBank",
    "IssuerBankABA": 21200025,
    "IssuerBankAccount": "BBPMTS",
}

pi_outter = build_PaymentInstruction(example_data)


def test_outer_node():
    """
    Checks if 'PaymentInstruction' node exists
    """
    assert "PaymentInstruction" in pi_outter


pi = pi_outter["PaymentInstruction"]


def test_payment_instruction_nodes():
    """
    This tests the PaymentInstruction build for a single entry.
    Checks if fields needed for Fargo file are created.
    """

    # checks if outer keys are there
    assert "PayeeDetails" in pi
    assert "PaymentInfo" in pi
    assert "ContextSource" in pi


def test_PayeeDetails():
    """
    Checks for valid PayeeDetail nodes and for
    nodes within PayeeDetails
    """
    # checks PayeeDetails keys
    PayeeDetailsKeys = pi["PayeeDetails"]
    assert "AnnuityPolicyId" in PayeeDetailsKeys
    assert "PayeeParty" in PayeeDetailsKeys
    assert "PaymentAnnotation" in PayeeDetailsKeys

    # checks PayeeDetails.PayeeParty keys
    PayeePartyKeys = pi["PayeeDetails"]["PayeeParty"]
    assert "FullName" in PayeePartyKeys
    assert "Address" in PayeePartyKeys

    # checks PayeeDetails.PayeeParty.Address keys
    AddressKeys = pi["PayeeDetails"]["PayeeParty"]["Address"]
    assert "Street" in AddressKeys
    assert "City" in AddressKeys
    assert "State" in AddressKeys
    assert "Zip" in AddressKeys


def test_PaymentInfo():
    """
    Checks for valid PaymentInfo nodes and for
    nodes within PaymentInfo nodes.
    """
    # checks PaymentInfo keys
    PaymentInfoKeys = pi["PaymentInfo"]
    assert "Payment" in PaymentInfoKeys

    # checks Payment keys
    PaymentKeys = pi["PaymentInfo"]["Payment"]
    assert "CurrencyAmount" in PaymentKeys
    assert "CurrencyInstrument" in PaymentKeys

    # checks Payment.CurrencyInstrument.Symbol existence
    CIKeys = pi["PaymentInfo"]["Payment"]["CurrencyInstrument"]
    assert "Symbol" in CIKeys


def test_ContextSource():
    """
    Checks for valid ContextSources nodes.
    """
    # checks ContextSource.Source existence
    CSKeys = pi["ContextSource"]
    assert "Source" in CSKeys
