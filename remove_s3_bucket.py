import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    s3_bucket = os.environ.get('S3_BUCKET', 'costmgmtacct1234')
    aws = AwsService()
    result = aws.delete_bucket(s3_bucket)

    if result:
        print(f'S3 bucket {s3_bucket} was deleted.')
    else:
        print(f'Failed deleting S3 bucket {s3_bucket}.')

main()
