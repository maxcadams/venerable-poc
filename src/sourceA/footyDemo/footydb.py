import json
import logging
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Club:
    """
    Encapsulates producer 1 data and operations into a single class
    We store 2 table, one containing match data for a club and one containing
    the finincial data for the club.

    Objct represents a club 'club_name' that is in the league 'league'
    """

    def __init__(self, dyn_resource, club_name, league):
        """
        :param dyn_resource: A boto3 DynamoDB resource
        """
        self.club_name = club_name
        self.league = league

        self.dyn_resource = dyn_resource
        self.table1 = None
        self.table2 = None

    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to financial data
        from football matches for club.

        :param table_name: The name of the table to create.
        :param id: Precondition: id can only equal 1 or 2
        :return: The newly created table.
        """

        try:
            if table_name == "transactions":
                self.table1 = self.dyn_resource.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                        {"AttributeName": "date", "KeyType": "RANGE"},  # Sort key
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "id", "AttributeType": "N"},
                        {"AttributeName": "date", "AttributeType": "S"},
                    ],
                    ProvisionedThroughput={"ReadCapacityUnits": 20, "WriteCapacityUnits": 20},
                )
                self.table1.wait_until_exists()
                return self.table1
            elif table_name == "matches":
                self.table2 = self.dyn_resource.create_table(
                    TableName=table_name,
                    KeySchema=[{"AttributeName": "date", "KeyType": "HASH"}],  # Partition key
                    AttributeDefinitions=[{"AttributeName": "date", "AttributeType": "S"}],
                    ProvisionedThroughput={"ReadCapacityUnits": 20, "WriteCapacityUnits": 20},
                )
                self.table2.wait_until_exists()
                return self.table2

        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def add_transaction(self, transaction):
        # id, date, description, transaction_type, credit, debit):
        """
        Adds transactions to table1.

        :param date:        date of transaction
        :param description: description of transaction
        :param type:        type of transaction
        :param credit:      cost
        :param debit:       profit
        """
        try:
            response = self.table1.put_item(
                # Item={
                #     'id': id,
                #     'date': date,
                #     'description': description,
                #     'type': transaction_type,
                #     'credit': credit,
                #     'debit': debit
                #     }
                Item=transaction
            )
        except ClientError as err:
            logger.error(
                "Couldn't update transaction %d from date %s to table %s. Here's why: %s: %s",
                transaction["id"],
                transaction["date"],
                self.table1.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        return response

    def add_match(self, match_data):
        """
        Adds matches to table2.


        """
        try:
            response = self.table2.put_item(Item=match_data)
        except ClientError as err:
            logger.error(
                "Couldn't add match from data %s to table %s. Here's why: %s: %s",
                match_data["date"],
                self.table2.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        return response

    def get_transaction_data(self, file_name):
        """
        Takes in json object filename, converts to list of dictionaries.

        :param file_name: file name of json object
        :return: Transaction data as dict.
        """

        try:
            with open(file_name) as file:
                transaction_data = json.load(file, parse_float=Decimal)
        except FileNotFoundError:
            logger.error(f"File {file_name} not found.")
            raise

        else:
            return transaction_data

    def get_match_data(self, file_name):
        """
        Takes in json object filename, converts to list of dictionaries.

        :param file_name: file name of object
        :return: Match data as dict
        """

        try:
            with open(file_name) as file:
                matches_data = json.load(file, parse_float=Decimal)
        except FileNotFoundError:
            logger.error(f"File {file_name} not found.")
            raise

        return matches_data

    def add_transaction_data(self, file_name):
        """
        Adds sample data to table1.

        :param file_name: file name of json object with sample data.
        """
        transactions = self.get_transaction_data(file_name)
        for transaction in transactions:
            self.add_transaction(transaction)

            # transaction['id'], transaction['date'],
            #                  transaction['description'], transaction['type'],
            #                  transaction['credit'], transaction['debit'])

    def add_match_data(self, file_name):
        """
        Adds sample data to table2.

        :param file_name: file name of json object with match data
        """
        matches = self.get_match_data(file_name)
        for match in matches:
            self.add_match(match)

    def scan_transactions(self):
        scan_resp = self.table1.scan()
        return scan_resp["Items"]

    def scan_matches(self):
        scan_resp = self.table2.scan()
        return scan_resp["Items"]

    def delete_tables(self):
        """
        Deletes tables
        """
        try:
            self.table1.delete()
            self.table1 = None
            self.table2.delete()
            self.table2 = None
        except ClientError as err:
            logger.error(
                "Couldn't delete tables. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise


def run_scenario(dynamodb):
    Arsenal = Club(dyn, club_name="Arsenal", league="English Premier League")
    Arsenal.create_table("transactions")
    Arsenal.create_table("matches")
    Arsenal.add_transaction_data("transactions.json")
    Arsenal.add_match_data("matches.json")

    while True:
        msg = input("Say 'finish' to stop and delete tables, 'scan' to scan both tables: ")
        if msg == "finish":
            Arsenal.delete_tables()
            break
        elif msg == "scan":
            print(Arsenal.scan_matches())
            print(Arsenal.scan_transactions())


if __name__ == "__main__":
    dyn = boto3.resource("dynamodb")
    run_scenario(dyn)
