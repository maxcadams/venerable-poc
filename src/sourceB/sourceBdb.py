"""
For Venerable POC, Summer 2022

Creates s3 bucket that holds csv file that
holds sourceB data.

Author: Max Adams
"""

import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class sourceBdb:
    def __init__(self, s3_resource):
        self.s3 = s3_resource
        self.Bucket = None

    def create_bucket(self, bucket_name):
        """
        Create s3 bucket.

        :param bucket_name: name of bucket
        :return: AWS response after creating bucket.
        """
        try:
            response = self.s3.create_bucket(Bucket=bucket_name)
            self.Bucket = self.s3.Bucket(bucket_name)
            self.Bucket.wait_until_exists()
        except ClientError as err:
            logger.error("Couldn't create bucket %s.", bucket_name)
            raise err
        return response

    def delete_bucket(self):
        """
        Deletes s3 bucket attached to object.

        :return: AWS response to deleting bucket.
        """
        try:
            for item in self.Bucket.objects.all():
                self.s3.Object(self.Bucket.name, item.key).delete()
            response = self.Bucket.delete()
            self.Bucket = None
        except ClientError as err:
            logger.error("Couldn't delete bucket.")
            raise err
        return response

    def put_item(self, dir, obj_key):
        """
        Uploads file with path 'dir' and key 'obj-key' to bucket.

        :param dir: Path to file.
        :param obj_key: Key for file when added to s3 bucket.
        :return: AWS response to uploading file.
        """
        try:
            response = self.Bucket.upload_file(f"{dir}", f"{obj_key}")
        except ClientError as err:
            logger.error("Couldn't delete bucket.")
            raise err
        return response

    def list_items(self):
        """
        Lists items in bucket.
        """
        try:
            for item in self.Bucket.objects.all():
                print(item)
        except ClientError as err:
            logger.error("Couldn't list items in bucket.")
            raise err


def main():
    """
    Main routine. Here we configure the logger, then configure both file and
    bucket names. Creates a bucket, puts file into bucket, then prompts if you
    want to delete the bucket yet.
    """

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    s3 = boto3.resource("s3")
    sourceB = sourceBdb(s3)
    bucket_name = "source-b-bucket"
    file_name = "sourceB.csv"
    logger.info("Creating bucket '%s' ...", bucket_name)
    sourceB.create_bucket(bucket_name)
    logger.info("Created bucket '%s'", bucket_name)
    logger.info("Putting file '%s' ...", file_name)
    sourceB.put_item(file_name, file_name)
    logger.info("File put with key '%s'.", file_name)
    while True:
        prompt = input(
            "Type 'finish' to delete bucket and end process, \
type 'list' to list items: "
        )
        if prompt == "finish":
            logger.info("Deleting bucket '%s'...", bucket_name)
            sourceB.delete_bucket()
            logger.info("Bucket deleted.")
            break
        if prompt == "list":
            sourceB.list_items()


if __name__ == "__main__":
    main()
