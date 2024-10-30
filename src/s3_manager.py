import requests
import os
import boto3
import json
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
            print(f"Bucket {self.bucket_name} is unique")
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
                object_name,
                ExtraArgs={
                    'ContentType': 'text/plain',  # Set appropriate content type
                    'ContentDisposition': 'inline'  # Optional, to display in-browser
                }
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
            
        """
        Setting The ACL Enabled But In Case you use Bucket Policy you should Disable it 
        """
    # def put_bucket_ownership_controls(self):
    #     response = self.s3_client.put_bucket_ownership_controls(
    #         Bucket=self.bucket_name,
    #         OwnershipControls={
    #             'Rules': [
    #                 {
    #                     'ObjectOwnership': 'BucketOwnerPreferred'
    #                 },
    #             ]
    #         }
    #     )
    #     return response

    def set_public_access_block(self):
        response = self.s3_client.put_public_access_block(
            Bucket=self.bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': False
            }
        )
        return response
    
    """
    Setting The ACL Read for Objects to Public But In Case you use Bucket Policy you should Disable it 
    """
    # def allow_public_access_to_file(self, file_name):
    #     """
    #     Make a specific file publicly accessible
    #     :param file_name: Name of the file to make public
    #     """
    #     try:
    #         response = self.s3_client.put_object_acl(
    #             Bucket=self.bucket_name,
    #             Key=file_name,
    #             ACL='public-read'
    #         )
    #         print(f"Successfully made {file_name} publicly accessible")
    #         # Get and print the public URL
    #         url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
    #         print(f"Public URL: {url}")
    #         return True
    #     except ClientError as e:
    #         print(f"Error setting file public access: {str(e)}")
    #         return False

    def set_bucket_policy(self, policy_file_path):
            """
            Set a bucket policy from a JSON file with dynamic bucket name insertion
            :param policy_file_path: Path to the JSON file containing the bucket policy
            """
            try:
                # Load the policy as a string
                with open(policy_file_path, 'r') as policy_file:
                    policy_string = policy_file.read()
                    my_ip= policy_file.read()
                
                try:
                    my_ip = requests.get('https://ipinfo.io/ip', timeout=5).text.strip()
                except requests.RequestException as e:
                    print(f"Error fetching IP address: {e}")
                    return None
                
                
                # Insert the actual bucket name dynamically
                policy_string = policy_string.replace("<bucket-name>", self.bucket_name)
                policy_string = policy_string.replace("<ip-address>", my_ip)

                # Parse the modified policy back into JSON format
                policy_json = json.loads(policy_string)
                

                # Apply the policy to the bucket
                response = self.s3_client.put_bucket_policy(
                    Bucket = self.bucket_name,
                    Policy = json.dumps(policy_json)
                )
                print(f"Successfully applied policy from {os.path.basename(policy_file_path)} to {self.bucket_name}")
                return response
            except FileNotFoundError:
                print(f"Policy file {policy_file_path} not found.")
                return None
            except ClientError as e:
                print(f"Error setting bucket policy: {e}")
                return None