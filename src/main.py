import os
from s3_manager import S3BucketManager
from datetime import datetime

def main():
    # Example usage

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    bucket_name = f'bucket-boto3-{timestamp}'  # Replace with your desired bucket name
    file_to_upload = r'C:\devpro\project\data\ID.png'  # Replace with your file path
    policy_file_path = r'C:\devpro\project\src\website_security_policy.json'

    # Initialize the S3 bucket manager
    s3_manager = S3BucketManager(bucket_name)
    
    # Create the bucket if it doesn't exist
    if not s3_manager.check_bucket_exists():
        if s3_manager.create_bucket():
            print(f"Created new bucket: {bucket_name}")
        else:
            print("Failed to create bucket")
            return

    # Upload a file
    if s3_manager.upload_file(file_to_upload):
        print("File upload successful")
    else:
        print("File upload failed")

    # List bucket contents
    s3_manager.list_bucket_contents()

    #Enable ACL Ownership to the Bucket
    # s3_manager.put_bucket_ownership_controls()

    #Disable Block Public Access
    s3_manager.set_public_access_block()

    # Enable ACL to read public access to the object
    # s3_manager.allow_public_access_to_file(os.path.basename(file_to_upload))

    # Attach a Policy to an S3 Bucket
    s3_manager.set_bucket_policy(policy_file_path)


if __name__ == "__main__":
    main()