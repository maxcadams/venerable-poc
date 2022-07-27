"""
For Venerable POC, Summer 2022

Script that translates data from calling orch
to a Bank model and adds to csv file that is
locally stored into 'sheets/{file_name}  and also
stored into an s3 bucket.

Author: Max Adams
"""

import csv
import json
import logging
import os
import random
import sys
from datetime import date, datetime

import boto3
import urllib3
from botocore.exceptions import ClientError

sys.path.append("..")
from helper_package.lookup import lookup

logger = logging.getLogger(__name__)

# gets orch endpoint
with open("orch_url.txt") as file:
    line = file.readline()
    orch_url = line[line.index("h"):].rstrip("\n")


def get_orch_data(url):
    """
    Gets data from orchestrator.

    :param url: API endpoint for orchestrator.
    :return: Response body as dict. Returns the PaymentInstructions list.
    """
    # PoolManager manges connection
    http = urllib3.PoolManager()
    HTTPres = http.request("GET", url)
    # convert to string
    response = HTTPres.data.decode("utf-8")
    body = json.loads(response)

    return body["Transactions"]["PaymentInstructions"]


def create_file():
    """
    Creates csv file for batch data

    :return: file descriptor for file we ar creating
    """
    now = datetime.now()

    now_str = now.strftime("%Y.%m.%d.%H.%M.%S")
    file_name = now_str + ".Bank.Payments.csv"

    return open(file_name, "w+", encoding="UTF8", newline="")


def add_data(transactions, file):
    """
    Creates file and add data from transactions to csv file in one batch
    in bank format.

    :param transactions: Input transactions being put into csv file.
    :param file: File descriptor for file that we are adding data to.
                 (Should be .csv)
    """
    field_names = [
        "BatchID",
        "SequenceID",
        "BatchDate",
        "PolicyNum",
        "PayeeFullName",
        "PayeeStreet",
        "PayeeCity",
        "PayeeState",
        "PayeeZipcode",
        "Account",
        "Comments",
        "Amount",
        "Currency",
        "SourceSystem",
    ]

    # with create_file() as file:
    writer = csv.writer(file)

    # write headers in
    writer.writerow(field_names)
    sequenceIdCounter = 1
    batchId = random.randint(1, 9999)
    for transaction in transactions:
        pi = transaction["PaymentInstruction"]
        row = [
            batchId,  # BatchID .... do we want uuid or random num
            sequenceIdCounter,  # SequenceID
            date.today().strftime("%Y%m%d"),  # BatchDate
            pi["PayeeDetails"]["AnnuityPolicyId"],  # PolicyNum
            pi["PayeeDetails"]["PayeeParty"]["FullName"],  # PayeeFullName
            pi["PayeeDetails"]["PayeeParty"]["Address"]["Street"],  # PayeeStreet
            pi["PayeeDetails"]["PayeeParty"]["Address"]["City"],  # PayeeCity
            pi["PayeeDetails"]["PayeeParty"]["Address"]["State"],  # PayeeState
            pi["PayeeDetails"]["PayeeParty"]["Address"]["Zip"],  # PayeeZipcode
            lookup("CompanyCheckAccount", "BigBankAccounts", "Account.json"),  # Account
            pi["PayeeDetails"]["PaymentAnnotation"],  # Comments
            pi["PaymentInfo"]["Payment"]["CurrencyAmount"],  # Amount
            pi["PaymentInfo"]["Payment"]["CurrencyInstrument"]["Symbol"],  # Currency
            pi["ContextSource"]["Source"],  # SourceSystem
        ]
        writer.writerow(row)

        # increment sequence id
        sequenceIdCounter += 1


def create_bucket(s3, bucket_name):
    """
    Create s3 bucket.
    :param s3: resource input for bucket
    :param bucket_name: name of bucket
    :return: S3 bucket with bucket_name.
    """
    try:
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as error:
        logger.error("Couldn't create bucket named '%s'", bucket_name)
        raise error

    return s3.Bucket(bucket_name)


def delete_bucket(s3, bucket):
    """
    Delete s3 bucket along with contents inside.
    :param s3: resource input for bucket
    :param bucket: bucket object that we are deleting.
    """
    try:
        for item in bucket.objects.all():
            s3.Object(bucket.name, item.key).delete()
        bucket.delete()
    except ClientError as error:
        logger.error("Couldn't delete bucket named '%s'", bucket.name)
        raise error


def main():
    """
    Main routine.
    Creates csv file, adds data from calling orch endpoint,
    then places into s3 bucket too.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("Creating file...")
    file_name = ""
    with create_file() as file:
        try:
            add_data(get_orch_data(orch_url), file)
            file_name = file.name
        except KeyError: # if something wrong with service, deletes trash
            os.remove(file_name)

    # creates new dir and moves file into it
    new_dir = r"sheets"
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, new_dir)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    os.replace(f"{current_directory}/{file_name}", f"{final_directory}/{file_name}")
    logger.info("File '%s' created. Moved to directory '%s'", file_name, new_dir)

    logger.info("Creating s3 bucket...")
    # creates s3 bucket
    s3 = boto3.resource("s3")
    bucket_name = "bigbank-consumer-bucket"
    bucket = create_bucket(s3, bucket_name)
    bucket.upload_file(f"{new_dir}/{file_name}", f"{file_name}")
    logger.info("File with obj-key '%s' upload to s3 bucket '%s'. ", file_name, bucket_name)

    while True:
        prompt = input("Type 'finish' to delete bucket and end process: ")
        if prompt == "finish":
            logger.info("Deleting bucket...")
            break
    delete_bucket(s3, bucket)
    logger.info("Bucket '%s' deleted.", bucket_name)


if __name__ == "__main__":
    main()
