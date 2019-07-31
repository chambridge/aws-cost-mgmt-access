import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    region = os.environ.get('REGION', 'us-east-1')
    s3_bucket = os.environ.get('S3_BUCKET', 'costmgmtacct1234')
    cost_report = os.environ.get('COST_REPORT', 'creport')
    aws = AwsService()

    result = aws.create_cost_usage_report(cost_report, s3_bucket, region)
    if result:
        print(f'Cost usage report {cost_report} was created.')
    else:
        print(f'Failed creating cost usage report {cost_report}.')

main()