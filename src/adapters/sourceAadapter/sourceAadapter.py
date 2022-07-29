"""
For Venerable POC, Summer 2022

Contains lambda handler and helper functions
for sourceA data.

Pulls data from dynamodb table and adapts 
data to domain model.

Author: Max Adams
"""

import json
import os
import sys

import boto3

sys.path.append("../..")
from helper_package import decimalencoder
from helper_package.lookup import lookup

dynamodb = boto3.resource("dynamodb")


def build_PayeeDetails(transaction):
    """
    Builds the PayeeDetails section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PayeeDetails section.
    """
    PayeeDetails = {}
    PayeeDetails["AnnuityPolicyId"] = transaction["ContractNum"]

    if transaction["AnnuitantName"] != "":
        PayeeDetails["PayeePolicyRole"] = "ANNUITANT"
        alias = transaction["AnnuitantName"]
    elif transaction["BeneficiaryName"] != "":
        PayeeDetails["PayeePolicyRole"] = "BENEFICIARY"
        alias = transaction["BeneficiaryName"]
    else:  # OtherPayeeName != ""
        PayeeDetails["PayeePolicyRole"] = "OTHER"
        alias = transaction["OtherPayeeName"]

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
        alias=transaction["IssuerBankName"],
        alias_set="BankingInstitutions",
        lookup_file="BankParty.json",
    )
    PaymentInfo["PaymentIssuerBankAccount"] = lookup(
        alias=transaction["IssuerBankAccount"],
        alias_set="BankAccounts",
        lookup_file="Account.json",
    )
    PaymentInfo["IntendedPaymentIssuerBankPostingDate"] = transaction["BatchDate"]
    PaymentInfo["PaymentTransactionId"] = transaction["id"]

    payment = {}
    payment["PaymentMechanism"] = "CHECK"  # hardcoded to CHECK bc all entries are TransType CHK
    payment["CurrencyAmount"] = transaction["Amount"][1:]  # don't want the '$'
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
    clp["IntendedGeneralLedgerPostingDate"] = transaction["BatchDate"]
    clp["PaymentCompanyParty"] = lookup(
        alias=transaction["CompanyId"],
        alias_set="CompanyCompanies",
        lookup_file="OrganizationParty.json",
    )
    clp["PaymentCompanyGeneralLedgerAccount"] = lookup(
        alias="COMPPMT", alias_set="BankAccounts", lookup_file="Account.json"
    )

    return clp


def build_ContextSource(transaction):
    """
    Builds the ContextSource section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: ContextSource section.
    """
    ContextSource = {}
    ContextSource["Source"] = transaction["SourceId"]
    # need to decode Enum(WC=>OFFICE, DSM=>SITE)
    ContextSource["TriggeringPaymentEventLocation"] = (
        "OFFICE" if transaction["Site"] == "WC" else "SITE"
    )
    ContextSource["TriggeringPaymentEventID"] = transaction["ClaimNum"]
    ContextSource["TriggeringPaymentEventDatetime"] = None  # ask about this
    ContextSource["TriggeringPaymentEventBatchCycleId"] = transaction["BatchId"]
    ContextSource["TriggeringPaymentEventBatchCycleDatetime"] = transaction["BatchDate"]

    # for getting TriggeringPaymentEvent of TransactionCd and decoding
    # to Enum (WTH=WITHDRAWAL,
    #         DTH=DEATH_BENEFIT,
    #         CHRG=SURRENDER_CHARGE,
    #         BONUS=BONUS_RECAPTURE,
    #         MVA=MARKET_VALUE_ADJ,
    #         TRA=TOTAL_RETURN_ADJ)
    tcd = transaction["TransactionCd"]
    if tcd == "WTH":
        ContextSource["TriggeringPaymentEvent"] = "WITHDRAWAL"
    elif tcd == "DTH":
        ContextSource["TriggeringPaymentEvent"] = "DEATH_BENEFIT"
    elif tcd == "CHRG":
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
    :return: Created payment instruction.
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


def adapt(event, context):
    """
    Lambda function for aws.

    Pulls data from dynamodb, then builds
    domain model.
    """

    table = dynamodb.Table(os.environ["TABLE"])

    table_scan = table.scan()
    transactions = table_scan["Items"]

    domain = build_domain(transactions)

    response = {"statusCode": 200, "body": json.dumps(domain, cls=decimalencoder.DecimalEncoder)}

    return response
