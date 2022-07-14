import json
import os
from typing import List
from unicodedata import decimal
from decimal import Decimal
import decimalencoder
import boto3
import pprint


dynamodb = boto3.resource('dynamodb')

def create_domain_entry():
    domain = {}
    league = domain['league'] = {
        'name': 'English Premier League', 
        'club': {}
    }
    club = domain['league']['club'] = {
        'name': 'Arsenal FC',
        'city': 'London',
        'owner': 'E. Stanley Kroenke',
        'matches': []
    }
    return domain

def create_match_entry(HomeTeam, VisitingTeam, ScoreHomeTeam, ScoreVisitingTeam, 
                       DateOfMatch, MatchLocation):
    match = {
        'HomeTeam': HomeTeam,
        'VisitingTeam': VisitingTeam,
        'ScoreHomeTeam': ScoreHomeTeam,
        'ScoreVisitingTeam': ScoreVisitingTeam,
        'DateOfMatch': DateOfMatch,
        'MatchLocation': MatchLocation,
        'Revenue': Decimal(0), #for sake of simplicity, gonna have just a number entry for both
        'Expenses': Decimal(0)
        }
    return match

# def create_revenue_match(TicketType, TicketSales, ConcessionType, ConcessionSales):
#     revenue = {
#         'Ticket':{
#             'TicketType': TicketType,
#             'TicketSales': TicketSales
#         },
#         'Concessions': {
#             'ConcessionType': ConcessionType,
#             'ConcessionSales': ConcessionSales
#         }
#     }
#     return revenue

# def create_expenses_match(PlayerWages):
#     expenses = {
#         'PlayerSalary': PlayerWages
#     }
    
#     return expenses


def adapt_helper(transactions: list, matches : list) -> dict:
    """
    Sorts inputted data from database into the a dictionary matching 
    the domain model structure provided.

    :param transactions: input transactions
    :param matches: input matches
    """
    # constructs first two levels, now was to fill
    # in the match data
    domain = create_domain_entry()
    
    match_list = domain['league']['club']['matches'] #empty initially
    for match in matches:
        #creates matches entry for domain 
        date = match['date']
        match_entry = create_match_entry(match['Home'], match['Away'], match['HomeGoals'],
                        match['AwayGoals'], date, match['Stadium'])

        # now go through each transaction that correspond to that match (date)
        # below, transactions_list filtered 
        transactions_list = list(filter(lambda trans: trans['date'] == date, transactions))
        
        total_revenue = Decimal(0)
        total_expenses = Decimal(0)

        for transaction in transactions_list:
            if 'credit' in transaction:
                total_expenses += Decimal(transaction['credit'])
            
            if 'debit' in transaction:
                total_revenue += Decimal(transaction['debit'])
        
        #Edit revenue and expenses field and append
        match['Revenue'] = total_revenue
        match['Expenses'] = total_expenses
        match_list.append(match)        
    
    return domain
    




def adapt(event, context):
    
    table1 = dynamodb.Table(os.environ['TRANSACTIONS_TABLE'])  # type: ignore
    table2 = dynamodb.Table(os.environ['MATCHES_TABLE'])  # type: ignore

    transactions_scan = table1.scan() #type dict
    matches_scan = table2.scan()


    transactions = transactions_scan['Items'] #type list (of dicts)
    matches = matches_scan['Items']

    domain_formatted = adapt_helper(transactions, matches)
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Credentials': True
        },
        "body": f"{json.dumps(domain_formatted, cls=decimalencoder.DecimalEncoder)}"
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
    with open('transactions.json') as t_file:
        transactions = json.load(t_file, parse_float=Decimal)
    
    with open('matches.json') as m_file:
        matches = json.load(m_file, parse_float=Decimal)
    
    
    pprint.pprint(adapt_helper(transactions, matches))