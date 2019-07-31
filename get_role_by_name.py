import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""

    cost_role = os.environ.get('COST_ROLE', 'cost_mgmt')
    aws = AwsService()

    result = aws.get_iam_role(cost_role)
    if result:
        print(f'Successfully created role {cost_role} with ARN {result}')
    else:
        print(f'Failed to retrieve role {cost_role}.')

main()