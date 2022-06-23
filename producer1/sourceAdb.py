"""
Source A DB interface for Venerable POC
Summer 2022

author: Max Adams
"""

from asyncio.base_futures import _FINISHED
from decimal import Decimal
import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import pprint
# from botocore.errorfactory import ResourceInUseException

logger = logging.getLogger(__name__)

class SourceA:
    """
    Encapsulates data for source A into one table.
    
    """
    def __init__(self, dyn_resource):
        self.dyn_resource = dyn_resource
        self.table = None

    def create_table(self, table_name):
        """
        Creates Amazon DynamoDB table stores transactions data. 
        Stores it in the table field of class.

        :param table_name: Name of table we are creating.
        :return: table object
        """
        try: #ask ab key schema
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'} # partition key, subject to change
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 20, 'WriteCapacityUnits': 20})

            print("Creating table...")    
            self.table.wait_until_exists()
        except ClientError as err:
            if(err.response['Error']['Code'] == 'ResourceInUseException'):
                print("Table was already created! ... continuing process")
                self.table = self.dyn_resource.Table(table_name)
            else:
                logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
                raise

        
        print("Table created!")
        return self.table


    def add_transaction(self, transaction):
        """
        Adds transaction to table

        :param transaction: Transaction data being added.
        :return: reponse from putting item
        """

        try:
            response = self.table.put_item(
                Item=transaction
            )
        except ClientError as err:
            logger.error(
                "Couldn't update transaction %d to table %s. Here's why: %s: %s",
                transaction['id'], self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

        return response
    
    def get_transaction_data(self, file_name):
        """
        Takes in json object filename, converts to list of dictionaries.

        :param file_name: file name of json object
        :return: Transaction data as dict. (or list of dicts)
        """

        try:
            with open(file_name) as file:
                transaction_data = json.load(file, parse_float=Decimal)
        except FileNotFoundError:
            logger.error(f"File {file_name} not found.")
            raise
        
        return transaction_data

    def add_transaction_data(self, file_name):
        """
        Adds source data from file to table.

        :param file_name: file name of json object with sample data
        """
        transactions = self.get_transaction_data(file_name)
        print("Adding transaction data...")
        for transaction in transactions:
            self.add_transaction(transaction)

        print("Transaction data added!")

    def scan_transactions(self):
        """
        Returns list of items in table
        """
        response = self.table.scan()
        return response['Items']
    
    def delete_table(self):
        """
        Deletes table.
        """
        try:
            print("Deleting tables...")
            self.table.delete()
            self.table = None
            print("Table deleted.")
        except ClientError as err:
            logger.error(
                "Couldn't delete tables. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

def main():
    dyn = boto3.resource('dynamodb')
    sourceA = SourceA(dyn)

    sourceA.create_table('sourceA-transactions')
    sourceA.add_transaction_data('sourceA.json')

    while True:
        msg = input("Say 'finish' to stop and delete tables, 'scan' to scan both tables: ")
        if msg == 'finish':
            sourceA.delete_table()
            break
        elif msg == 'scan':
            pprint.pprint(sourceA.scan_transactions())


if __name__ == '__main__':
    main()