import os

from cloud.aws_service import AwsService

def main():
    """Execute script."""
    aws = AwsService()

    result = aws.list_cost_usage_reports()
    if result:
        print(f'Cost usage reports:')
        for report in result:
            print(report)
    else:
        print(f'Failed to list cost usage reports.')

main()