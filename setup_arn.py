import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    s3_bucket = os.environ.get('S3_BUCKET', 'costmgmtacct1234')
    cost_policy = os.environ.get('COST_POLICY', 'cost_mgmt')
    cost_role = os.environ.get('COST_ROLE', 'cost_mgmt')
    share_account = os.environ.get('SHARE_ACCOUNT')
    if share_account is None:
        print('You must set the SHARE_ACCOUNT environment variable.')
        exit(1)

    aws = AwsService()
    result = aws.create_cost_arn(cost_policy, s3_bucket, cost_role, share_account)

    if result:
        print(f'Cost ARN {result} was created.')
    else:
        print(f'Failed creating cost ARN.')

main()