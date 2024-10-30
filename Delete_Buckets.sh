#Delete Buckets that start with specific string

for bucket in $(aws s3api list-buckets --query "Buckets[?starts_with(Name, 'bucket-boto3')].Name" --output text); do
    # Empty the bucket (delete all objects inside it)
    aws s3 rm s3://$bucket --recursive
    
    # Delete the bucket itself
    aws s3api delete-bucket --bucket $bucket
    
    echo "Deleted bucket: $bucket"
done