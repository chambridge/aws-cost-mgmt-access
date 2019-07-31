import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    cost_policy = os.environ.get('COST_POLICY', 'cost_mgmt')
    aws = AwsService()

    result = aws.delete_iam_policy(cost_policy)
    if result:
        print(f'Successfully deleted policy {cost_policy}')
    else:
        print(f'Failed to delete policy {cost_policy}.')

main()