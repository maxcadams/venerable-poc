import json
import decimalencoder
import os
import boto3
from decimal import Decimal

"""
Lambda handler that takes in data from sourceA and adapts it to domain model
schema. 

Right now, we should perform all of the look up files, 
then start building from the inside and move out.

BE AS LAZY AS POSSIBLE (when coding)
-- with lookups, try to make it a single function

-- break down building model structure into several no-input functions

"""

def lookup(alias, alias_set):
    """
    Performs a party look up by alias in alias_set.

    :param alias: Alias of party we are looking up.
    :param alias_set: Alias set in which party resides.
    :return: Party information
    """
    pass

def build_PayeeDetails(transaction):
    """
    Builds the PayeeDetails section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PayeeDetails section.
    """
    pass


def build_PaymentInfo(transaction):
    """
    Builds the PaymentInfo section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PaymentInfo section.
    """
    pass

def build_VLP(transaction):
    """
    Builds the VenerableLedgerProcessing section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: VLP section.
    """
    vlp = {}
    vlp['PaymentCompanyCostCenter'] = transaction['CostCenter']
    vlp['IntendedGeneralLedgerPostingDate'] = transaction['BatchDate']
    

def build_ContextSource(transaction):
    """
    Builds the ContextSource section of a PaymentInstruction. 

    :param transaction: Transaction data being used to build section.
    :return: ContextSource section.
    """
    ContextSource = {}
    ContextSource['Source'] = transaction['SourceId']
    # need to decode Enum(WC=>OFFICE, DSM=>SITE)
    ContextSource['TriggeringPaymentEventLocation'] = 'OFFICE' if transaction['Site'] == 'WC' else 'SITE'
    ContextSource['TriggeringPaymentEventID'] = transaction['ClaimNum']
    ContextSource['TriggeringPaymentDatetime'] = None #ask about this
    ContextSource['TriggeringPaymentEventBatchCycleId'] = transaction['BatchId']
    ContextSource['TriggeringPaymentEventBatchCycleDatetime'] = transaction['Batch Date']
    
    # for getting TriggeringPaymentEvent of TransactionCd and decoding
    # to Enum (WTH=WITHDRAWAL,
    #         DTH=DEATH_BENEFIT,
    #         CHRG=SURRENDER_CHARGE,
    #         BONUS=BONUS_RECAPTURE,
    #         MVA=MARKET_VALUE_ADJ,
    #         TRA=TOTAL_RETURN_ADJ)
    tcd = transaction['TransactionCd']
    if tcd == 'WTH':
        ContextSource['TriggeringPaymentEvent'] = 'WITHDRAWAL'
    elif tcd == 'DTH':
        ContextSource['TriggeringPaymentEvent'] = 'DEATH_BENEFIT'
    elif tcd == 'CHRG':
        ContextSource['TriggeringPaymentEvent'] = 'SURRENDER_CHARGE'
    elif tcd == 'BONUS':
        ContextSource['TriggeringPaymentEvent'] = 'BONUS_RECAPTURE'
    elif tcd == 'MVA':
        ContextSource['TriggeringPaymentEvent'] = 'MARKET_VALUE_ADJ'
    elif tcd == 'TRA':
        ContextSource['TriggeringPaymentEvent'] = 'TOTAL_RETURN_ADJ'
    
    return ContextSource
    

    
     

def build_PaymentInstruction(transaction, payment_instructions):
    """
    Builds payment instruction item using transaction and appends it 
    to payment_instructions.

    :param transaction: Transaction entry from source.
    :param payment_instructions: List of payment_instructions.
    :return: updated payment instructions --> is this necessary???
    """
    pi = {
        "PaymentInstruction": {}
    }
    PaymentInstruction = pi['PaymentInstruction']
    PaymentInstruction['ContextSource'] = build_ContextSource(transaction)
    PaymentInstruction['VenerableLedgerProcessing'] = build_VLP(transaction)
    PaymentInstruction['PaymentInfo'] = build_PaymentInfo(transaction)
    PaymentInstruction['PayeeDetails'] = build_PayeeDetails(transaction)
    
    payment_instructions.append(pi)
    return

def build_domain():
    """
    Builds outer skeleton of domain for payment instructions.
    """
    transactions = {
        'Transactions': {
            'SchemaVersion': 'v1.0',
            'PaymentInstructions': []
        }
    }
    
    payment_instructions : list = transactions['Transactions']['PaymentInstructions']
    
    return transactions


def adapt(event, context):
    
    response = {
        "statusCode": 200,
        "body": json.dumps()
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
