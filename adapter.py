import json
import os
from typing import List
from unicodedata import decimal
import decimalencoder
import boto3


dynamodb = boto3.resource('dynamodb')

def create_domain_entry():
    domain = {}
    league = domain['league'] = {
        'name': 'English Premier League', 
        'club': {}
    }
    club = domain['League']['club'] = {
        'name': 'Arsenal FC',
        'City': 'London',
        'Owner': 'E. Stanley Kroenke',
        'Matches': []
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
        'Revenue': {},
        'Expenses': {}
        }
    return match

def create_revenue_match(TicketType, TicketSales, ConcessionType, ConcessionSales):
    revenue = {
        'Ticket':{
            'TicketType': TicketType,
            'TicketSales': TicketSales
        },
        'Concessions': {
            'ConcessionType': ConcessionType,
            'ConcessionSales': ConcessionSales
        }
    }
    return revenue

def create_expenses_match(PlayerWages):
    expenses = {
        'PlayerSalary': PlayerWages
    }
    
    return expenses


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
        transactions_list = list(filter(lambda trans: trans['date'] == date), transactions)
        
        total_ticket_sales = 0
        total_concession_sales = 0
        total_player_wages = 0


        for transaction in transactions_list:
            if transaction.has_key('credit'):
                if transaction['type'] == 'Pwages':
                    total_player_wages+=transaction['credit']
            
            if transaction.has_key('debit'):
                


        
                        
            
    



def adapt(event, context):
    
    table1 = dynamodb.Table(os.environ['TRANSACTIONS_TABLE'])
    table2 = dynamodb.Table(os.environ['MATCHES_TABLE'])

    transactions_scan = table1.scan() #type dict
    matches_scan = table2.scan()


    transactions = transactions_scan['Items'] #type list (of dicts)
    matches = matches_scan['Items']

    response = {
        "statusCode": 200,
        "body": f"""{{
            "transactions":{json.dumps(transactions, cls=decimalencoder.DecimalEncoder)},
            "matches":{json.dumps(matches, cls=decimalencoder.DecimalEncoder)},
            }}"""
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
