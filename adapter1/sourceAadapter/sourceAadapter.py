import json
from typing import final
import decimalencoder
import os
import boto3
from decimal import Decimal
import pprint

"""
Lambda handler that takes in data from sourceA and adapts it to domain model
schema. 

Right now, we should perform all of the look up files, 
then start building from the inside and move out.

BE AS LAZY AS POSSIBLE (when coding)
-- with lookups, try to make it a single function

-- break down building model structure into several no-input functions

"""
dynamodb = boto3.resource('dynamodb')


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



def build_PayeeDetails(transaction):
    """
    Builds the PayeeDetails section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PayeeDetails section.
    """
    PayeeDetails = {}
    PayeeDetails['AnnuityPolicyId'] = transaction['ContractNum']
    

    if transaction['AnnuitantName'] != "":
        PayeeDetails['PayeePolicyRole'] = 'ANNUITANT'
        alias = transaction['AnnuitantName']
    elif transaction['BeneficiaryName'] != "":
        PayeeDetails['PayeePolicyRole'] = 'BENEFICIARY'
        alias = transaction['BeneficiaryName']
    else: #OtherPayeeName != ""
        PayeeDetails['PayeePolicyRole'] = 'OTHER'
        alias = transaction['OtherPayeeName']
    
    PayeeDetails['PayeeParty'] = lookup(alias=alias, alias_set='Payees', 
    lookup_file='PersonParty.json')

    PayeeDetails['PaymentAnnotation'] = transaction['Message']

    return PayeeDetails        
    


def build_PaymentInfo(transaction):
    """
    Builds the PaymentInfo section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PaymentInfo section.
    """
    PaymentInfo = {}
    PaymentInfo['PaymentIssuerBankParty'] = lookup(alias=transaction['IssuerBankName'], 
    alias_set='BankingInstitutions', lookup_file='BankParty.json')
    PaymentInfo['PaymentIssuerBankAccount'] = lookup(alias=transaction['IssuerBankAccount'],
    alias_set='BankAccounts', lookup_file='Account.json')
    PaymentInfo['IntendedPaymentIssuerBankPostingDate'] = transaction['BatchDate']
    PaymentInfo['PaymentTransactionId'] = transaction['id']
    
    payment = {}
    payment['PaymentMechanism'] = 'CHECK' #hardcoded to CHECK bc all entries are TransType CHK
    payment['CurrencyAmount'] = transaction['Amount'][1:] #don't want the '$'
    payment['CurrencyInstrument'] = lookup(alias=None, 
    alias_set=None, lookup_file='Instrument.json')
    
    PaymentInfo['Payment'] = payment

    return PaymentInfo


    


def build_VLP(transaction):
    """
    Builds the VenerableLedgerProcessing section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: VLP section.
    """
    vlp = {}
    vlp['PaymentCompanyCostCenter'] = transaction['CostCenter']
    vlp['IntendedGeneralLedgerPostingDate'] = transaction['BatchDate']
    vlp['PaymentCompanyParty'] = lookup(alias=transaction['CompanyId'], 
    alias_set='VenerableCompanies', lookup_file='OrganizationParty.json')
    vlp['PaymentCompanyGeneralLedgerAccount'] = lookup(alias='VIACPMT', 
    alias_set='BankAccounts', lookup_file='Account.json')
    
    return vlp
    

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
    ContextSource['TriggeringPaymentEventBatchCycleDatetime'] = transaction['BatchDate']
    
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

def build_domain(transactions : list):
    """
    Builds outer skeleton of domain for payment instructions.

    :param transactions: transactions from sourceA (list)
    """
    final = {
        'Transactions': {
            'SchemaVersion': 'v1.0',
            'PaymentInstructions': []
        }
    }
    
    payment_instructions : list = final['Transactions']['PaymentInstructions']
    
    for transaction in transactions:
        build_PaymentInstruction(transaction, payment_instructions)


    return final


def adapt(event, context):
    
    table = dynamodb.Table(os.environ['TABLE'])

    table_scan = table.scan()
    transactions = table_scan['Items']

    domain = build_domain(transactions)

    response = {
        "statusCode": 200,
        "body": json.dumps(domain, cls=decimalencoder.DecimalEncoder)
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


if __name__ == '__main__':
    with open('sourceA.json') as file:
        entries = json.load(file, parse_float=Decimal)
        
    domain = build_domain(entries)
    
    with open('output.json', 'w') as output:
        json.dump(domain, output)

