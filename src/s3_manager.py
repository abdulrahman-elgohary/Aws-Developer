import os
import boto3
from botocore.exceptions import ClientError

# Attributes that are essential for any bucket
class S3BucketManager:
    def __init__(self, bucket_name, region='us-east-1'):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.s3_resource = boto3.resource('s3', region_name=self.region)

    def check_bucket_exists(self):
        """
        Check if a bucket exists and you have access to it
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            print(f"Bucket {self.bucket_name} is uniqe")
            return False
    
    def create_bucket(self):
        """
        Create an S3 bucket in a specified region
        """
        try:
            if self.region == 'us-east-1':
                # AWS defaults to us-east-1, it errors if you specify it explicitly
                response = self.s3_client.create_bucket(
                    Bucket=self.bucket_name
                )
            else:
                location = {'LocationConstraint': self.region}
                response = self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration=location
                )
            print(f"Successfully created bucket {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            return False

    def upload_file(self, file_path, object_name=None):
        """
        Upload a file to S3 bucket
        :param file_path: Path to the file to upload
        :param object_name: S3 object name Default to None (if different from file_path)
        """
        # If object_name not specified, use file_path
        if object_name is None:
            object_name = os.path.basename(file_path)


        try:
            response = self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                object_name
            )
            print(f"Successfully uploaded {file_path} to {self.bucket_name}/{object_name}")
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False

    

    def list_bucket_contents(self):
        """
        List all objects in the bucket
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                print(f"\nContents of bucket {self.bucket_name}:")
                for obj in response['Contents']:
                    print(f"- {obj['Key']}")
            else:
                print(f"\nBucket {self.bucket_name} is empty")
        except ClientError as e:
            print(f"Error listing bucket contents: {e}")

