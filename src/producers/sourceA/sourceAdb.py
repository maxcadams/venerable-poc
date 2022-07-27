"""
For Venerable POC, Summer 2022

Creates dynamodb table that contains
sourceA data.

Author: Max Adams
"""
import json
import logging
import pprint
from decimal import Decimal
from tokenize import String

import boto3
from botocore.exceptions import ClientError

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
        try:  # ask ab key schema
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"}  # partition key, subject to change
                ],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 20, "WriteCapacityUnits": 20},
            )

            self.table.wait_until_exists()
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceInUseException":
                logger.info("Table was already created! ... continuing process")
                self.table = self.dyn_resource.Table(table_name)
            else:
                logger.error(
                    "Couldn't create table %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        return self.table

    def add_transaction(self, transaction):
        """
        Adds transaction to table

        :param transaction: Transaction data being added.
        :return: reponse from putting item
        """

        try:
            response = self.table.put_item(Item=transaction)
        except ClientError as err:
            logger.error(
                "Couldn't update transaction %d to table %s. Here's why: %s: %s",
                transaction["id"],
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
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
        for transaction in transactions:
            self.add_transaction(transaction)

    def scan_transactions(self):
        """
        Returns list of items in table
        """
        response = self.table.scan()
        return response["Items"]

    def delete_table(self):
        """
        Deletes table.
        """
        try:
            self.table.delete()
            self.table = None
        except ClientError as err:
            logger.error(
                "Couldn't delete tables. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

def create_file(arn : str):
    """
    Creates table_arn.txt in sourceAadapter directory that 
    contains the table ARN so serverless.yml can use the resource.

    :param arn: ARN that we are inputting into text file.
    """
    with open('../../adapters/sourceAadapter/table_arn.txt', 'w') as file:
        file.write(arn)
    return file.name


def main():
    """
    Main routine for dynamodb table for sourceA transactions.

    Creates table, then adds data.
    Runs prompt that leaves table up until user decides to stop using.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    dyn = boto3.resource("dynamodb")
    sourceA = SourceA(dyn)
    table_name = "sourceA-transactions"

    logger.info("Creating table with table name '%s'.", table_name)
    sourceA.create_table(table_name)
    logger.info("Table '%s' created.", table_name)
    file_name = "sourceA.json"
    logger.info("Adding transactions form '%s' to table '%s'.", file_name, table_name)
    sourceA.add_transaction_data(file_name)
    logger.info("Transactions added to table '%s'.", table_name)

    file_name = create_file(sourceA.table.table_arn)
    logger.info("File '%s' created in 'src/adapters/sourceAadapter' directory!", file_name)

    while True:
        try:
            msg = input(
            "Type 'finish' to stop and delete tables,\n     'exit' to stop without deleting tables,\n\
     'scan' to scan both tables: ")
        
   
            if msg == "finish":
                logger.info("Deleting table '%s' ...", table_name)
                sourceA.delete_table()
                logger.info("Table '%s' deleted.", table_name)
                break
            elif msg == "scan":
                pprint.pprint(sourceA.scan_transactions())
            elif msg == "exit":
                break
        except EOFError: #have this because EOF input during bash script execution
            break



if __name__ == "__main__":
    main()
