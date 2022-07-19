# import json
# import logging
# import uuid

# import boto3
# from botocore.exceptions import ClientError

# # logger = logging.getLogger(__name__)
# bucket_name = "testing-s3-venny"
# s3 = boto3.resource("s3")
# s3.create_bucket(Bucket=bucket_name)

# bucket = s3.Bucket(bucket_name)
# #                 file_name  obj-key
# bucket.upload_file("text.txt", "text.txt")

# # delete object: s3.Object(bucket_name, obj-key).delete()
# # delete bucket: s3.Bucket(bucket_name).delete()

# # s3_resource.create_bucket(Bucket='test1')
# # s3_resource.list_buckets()
# # """
# # bucket = s3_resource.Bucket('yahyah')

# # bucket.create()
# # """
