"""
For Venerable POC, Summer 2022

Contains lambda handler and helper functions
for sourceB data.

Pulls data from csv file in s3 bucket and adapts
data to domain model.

Author: Max Adams
"""

import csv
import json
import os
import sys
import uuid

import boto3

sys.path.append("../..")
from helper_package import decimalencoder
from helper_package.lookup import lookup

s3 = boto3.resource("s3")


def build_PayeeDetails(transaction):
    """
    Builds the PayeeDetails section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PayeeDetails section.
    """
    PayeeDetails = {}
    PayeeDetails["AnnuityPolicyId"] = transaction["PolicyNum"]

    pt = transaction["PayeeType"]
    if pt == "ANN":
        PayeeDetails["PayeePolicyRole"] = "ANNUITANT"
    elif pt == "BEN":
        PayeeDetails["PayeePolicyRole"] = "BENEFICIARY"
    else:  # pt == "OTH"
        PayeeDetails["PayeePolicyRole"] = "OTHER"

    if transaction["PayeeMinit"] == "":
        alias = f"{transaction['PayeeFName']} {transaction['PayeeLName']}"
    else:
        alias = (
            f"{transaction['PayeeFName']} {transaction['PayeeMinit']} {transaction['PayeeLName']}"
        )

    PayeeDetails["PayeeParty"] = lookup(
        alias=alias, alias_set="Payees", lookup_file="PersonParty.json"
    )

    PayeeDetails["PaymentAnnotation"] = transaction["Message"]

    return PayeeDetails


def build_PaymentInfo(transaction):
    """
    Builds the PaymentInfo section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PaymentInfo section.
    """
    PaymentInfo = {}
    PaymentInfo["PaymentIssuerBankParty"] = lookup(
        alias=transaction["BankName"],
        alias_set="BankingInstitutions",
        lookup_file="BankParty.json",
    )
    PaymentInfo["PaymentIssuerBankAccount"] = lookup(
        alias=transaction["CompanyBankAccount"],
        alias_set="BankAccounts",
        lookup_file="Account.json",
    )
    PaymentInfo["IntendedPaymentIssuerBankPostingDate"] = transaction["CycleDate"]
    PaymentInfo["PaymentTransactionId"] = str(uuid.uuid4())

    payment = {}
    payment["PaymentMechanism"] = "CHECK"  # hardcoded to CHECK bc all entries are TransType CHK
    payment["CurrencyAmount"] = transaction["Amount"].strip()[
        1:
    ]  # don't want the '$' and gets rid of trailing whitespace
    payment["CurrencyInstrument"] = lookup(
        alias=None, alias_set=None, lookup_file="Instrument.json"
    )

    PaymentInfo["Payment"] = payment

    return PaymentInfo


def build_CLP(transaction):
    """
    Builds the CompanyLedgerProcessing section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: CLP section.
    """
    clp = {}
    clp["PaymentCompanyCostCenter"] = transaction["CostCenter"]
    clp["IntendedGeneralLedgerPostingDate"] = transaction["CycleDate"]
    clp["PaymentCompanyParty"] = lookup(
        alias=transaction["LegalEntity"],
        alias_set="CompanyCompanies",
        lookup_file="OrganizationParty.json",
    )
    clp["PaymentCompanyGeneralLedgerAccount"] = lookup(
        alias="COMP", alias_set="CompanyAccounts", lookup_file="Account.json"
    )

    return clp


def build_ContextSource(transaction):
    """
    Builds the ContextSource section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: ContextSource section.
    """
    ContextSource = {}
    ContextSource["Source"] = transaction["SystemId"]
    # need to decode Enum(WC=>OFFICE, DSM=>SITE)
    ContextSource["TriggeringPaymentEventLocation"] = (
        "OFFICE" if transaction["SiteId"] == "WC" else "SITE"
    )
    ContextSource["TriggeringPaymentEventID"] = transaction["Claim"]
    ContextSource["TriggeringPaymentEventDatetime"] = transaction[
        "SystemProcessDate"
    ]  # ask about this
    ContextSource["TriggeringPaymentEventBatchCycleId"] = transaction["BatchNum"]
    ContextSource["TriggeringPaymentEventBatchCycleDatetime"] = transaction["CycleDate"]

    # for getting TriggeringPaymentEvent of TransactionCd and decoding
    # to Enum (WITH=WITHDRAWAL,
    #         DEATH=DEATH_BENEFIT,
    #         CHARGE=SURRENDER_CHARGE,
    #         BONUS=BONUS_RECAPTURE,
    #         MVA=MARKET_VALUE_ADJ,
    #         TRA=TOTAL_RETURN_ADJ)
    tcd = transaction["TransactionCd"]
    if tcd == "WITH":
        ContextSource["TriggeringPaymentEvent"] = "WITHDRAWAL"
    elif tcd == "DEATH":
        ContextSource["TriggeringPaymentEvent"] = "DEATH_BENEFIT"
    elif tcd == "CHARGE":
        ContextSource["TriggeringPaymentEvent"] = "SURRENDER_CHARGE"
    elif tcd == "BONUS":
        ContextSource["TriggeringPaymentEvent"] = "BONUS_RECAPTURE"
    elif tcd == "MVA":
        ContextSource["TriggeringPaymentEvent"] = "MARKET_VALUE_ADJ"
    elif tcd == "TRA":
        ContextSource["TriggeringPaymentEvent"] = "TOTAL_RETURN_ADJ"

    return ContextSource


def build_PaymentInstruction(transaction):
    """
    Builds payment instruction item using transaction and appends it
    to payment_instructions.

    :param transaction: Transaction entry from source.
    :param payment_instructions: List of payment_instructions.
    :return: payment instruction created
    """
    pi = {"PaymentInstruction": {}}
    PaymentInstruction = pi["PaymentInstruction"]
    PaymentInstruction["ContextSource"] = build_ContextSource(transaction)
    PaymentInstruction["CompanyLedgerProcessing"] = build_CLP(transaction)
    PaymentInstruction["PaymentInfo"] = build_PaymentInfo(transaction)
    PaymentInstruction["PayeeDetails"] = build_PayeeDetails(transaction)

    return pi


def build_domain(transactions: list):
    """
    Builds outer skeleton of domain for payment instructions.

    :param transactions: transactions from sourceA (list)
    """
    final = {"Transactions": {"SchemaVersion": "v1.0", "PaymentInstructions": []}}

    # builds list using list comprehension
    final["Transactions"]["PaymentInstructions"] = [
        build_PaymentInstruction(transaction) for transaction in transactions
    ]

    return final


def convert(contents):
    """
    Converts csv file data to a list of dictionaries.
    Headers are keys for the dictionaries while rows of
    data are a single dictionary.

    :param file_name: Name of csv file.
    :return: List of dictionaries corresponding with data from input file.
    """
    pi_list = []

    reader = csv.reader(contents)
    headers = next(reader)

    for row in reader:
        pi = {}
        # assume len(headers) == len(row)
        for i in range(len(headers)):
            pi[headers[i]] = row[i]

        pi_list.append(pi)

    return pi_list


def adapt(event, context):
    """
    Lambda function for aws.

    Gets data from csv file in s3 bucket,
    converts data to python dict,
    then builds domain model.
    """
    with open('bucket_name.txt') as file:
        bucket_name = file.read()
    obj = s3.Object(bucket_name, "sourceB.csv")
    # gets data from 'sourceB.csv' and converts it to lists so convert fn
    # can iterate thru it with the csv reader
    contents = obj.get()["Body"].read().decode("utf-8").split("\r\n")

    transactions = convert(contents)
    domain = build_domain(transactions)

    response = {"statusCode": 200, "body": json.dumps(domain, cls=decimalencoder.DecimalEncoder)}

    return response
