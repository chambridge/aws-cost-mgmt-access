import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    cost_policy = os.environ.get('COST_POLICY', 'cost_mgmt')
    aws = AwsService()

    result = aws.get_iam_policy(cost_policy)
    if result:
        print(f'{result}')
    else:
        print(f'Failed to retrieve policy {cost_policy}.')

main()