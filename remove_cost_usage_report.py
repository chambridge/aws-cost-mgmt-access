import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    s3_bucket = os.environ.get('S3_BUCKET', 'costmgmtacct1234')
    cost_report = os.environ.get('COST_REPORT', 'creport')
    aws = AwsService()

    result = aws.delete_cost_usage_report(cost_report, s3_bucket)
    if result:
        print(f'Cost usage report {cost_report} was removed.')
    else:
        print(f'Failed removing cost usage report {cost_report}.')

main()