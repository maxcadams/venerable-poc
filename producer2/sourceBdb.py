import boto3
import logging
import uuid
from botocore.exceptions import ClientError
from numpy import source

logger = logging.getLogger(__name__)

class sourceBdb:
    def __init__(self, s3_resource):
        self.s3 = s3_resource
        self.Bucket = None

    def create_bucket(self, bucket_name):
        """
        Create s3 bucket.
        :param bucket_name: name of bucket
        """
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            self.Bucket = self.s3.Bucket(bucket_name)
            logger.info(
                "Creating bucket '%s' ...", bucket_name
            )
            self.Bucket.wait_until_exists()
            logger.info(
                "Created bucket '%s'", bucket_name
            )
        except ClientError as err:
            logger.error("Couldn't create bucket %s.", bucket_name)
            raise err
    
    def delete_bucket(self):
        """
        Deletes s3 bucket attached to object.
        """
        try:
            logger.info("Deleting bucket '%s'...", self.Bucket.name)
            for item in self.Bucket.objects.all():
                self.s3.Object(self.Bucket.name, item.key).delete()
            self.Bucket.delete()
            self.Bucket = None
            logger.info("Bucket deleted.")
        except ClientError as err:
            logger.error("Couldn't delete bucket.")
            raise err

    def put_item(self, dir, obj_key):
        """
        Uploads file with path 'dir' and key 'obj-key' to bucket.
        :param dir: Path to file.
        :param obj_key: Key for file when added to s3 bucket.
        """
        try:
            self.Bucket.upload_file(f'{dir}', f'{obj_key}')
        except ClientError as err:
            logger.error("Couldn't delete bucket.")
            raise err

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
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    s3 = boto3.resource('s3')
    sourceB = sourceBdb(s3)
    bucket_name = 'source-b-' + str(uuid.uuid4())
    sourceB.create_bucket(bucket_name)
    sourceB.put_item('sourceB.csv', 'sourceB.csv')
    while(True):
        prompt = input("Type 'finish' to delete bucket and end process, \
type 'list' to list items: ")
        if prompt == 'finish':
            sourceB.delete_bucket()
            break
        if prompt == 'list':
            sourceB.list_items()
    
if __name__ == '__main__':
    main()

    



        
        


