import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    cost_role = os.environ.get('COST_ROLE', 'cost_mgmt')
    aws = AwsService()

    result = aws.delete_iam_role(cost_role)
    if result:
        print(f'Successfully deleted role {cost_role}')
    else:
        print(f'Failed to delete role {cost_role}.')

main()