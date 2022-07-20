"""
Test sourceB adapter logic. 
To test, we only check the keys, not the data.

Author: Max Adams
"""

import pytest
from sourceBadapter import build_domain, convert

with open("tests/sourceB_test.csv") as file:
    contents = file.read().split("\n")
    transactions = convert(contents)
    domain = build_domain(transactions)


pi = domain["Transactions"]["PaymentInstructions"][0]["PaymentInstruction"]


def test_outer_node():
    """
    Checks if 'PaymentInstruction' node exists along with 'Transactions'
    """
    assert "Transactions" in domain
    assert "PaymentInstructions" in domain["Transactions"]


def test_payment_instruction_nodes():
    """
    This tests the PaymentInstruction build for a single entry.
    Checks if fields needed for file are created.
    """

    # checks if outer keys are there
    pi_keys = pi
    assert "PayeeDetails" in pi_keys
    assert "PaymentInfo" in pi_keys
    assert "ContextSource" in pi_keys


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
