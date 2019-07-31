import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    region = os.environ.get('REGION', 'us-east-1')
    s3_bucket = os.environ.get('S3_BUCKET', 'costmgmtacct1234')
    aws = AwsService()
    result = aws.create_bucket(s3_bucket, region)

    if result:
        print(f'S3 bucket {s3_bucket} was created.')
    else:
        print(f'Failed creating S3 bucket {s3_bucket}.')

main()
