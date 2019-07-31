import logging
import os
import json

import boto3
from botocore.exceptions import ClientError


class AwsService:
    """A class to handle interactions with the AWS services."""

    def __init__(self):
        """Establish connection information."""
        self.access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        if self.access_key and self.secret_key:
            self.credentials = {
                'aws_access_key_id': self.access_key,
                'aws_secret_access_key': self.secret_key
            }
        else:
            raise ValueError('AWS Service credentials are not configured.')

    def create_bucket(self, bucket_name, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """
        # Create bucket
        try:
            if region is None:
                s3_client = boto3.client('s3', **self.credentials)
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = boto3.client('s3', region_name=region, **self.credentials)
                s3_client.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_bucket(self, bucket_name):
        """Delete an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to delete
        :return: True if bucket deleted, else False
        """
        try:
            s3_client = boto3.client('s3', **self.credentials)
            s3_client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def _set_cur_bucket_policy(self, bucket_name):
        """Set bucket policy for cost usage reporting.

        :param bucket_name: Bucket to apply cur policy to.
        :return: True if policy applied, else False
        """
        resource = f'arn:aws:s3:::{bucket_name}'
        resource_wildcard = f'arn:aws:s3:::{bucket_name}/*'
        policy_dict = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {
                        'AWS': 'arn:aws:iam::386209384616:root'
                    },
                    'Action': [
                        's3:GetBucketAcl',
                        's3:GetBucketPolicy'
                    ],
                    'Resource': resource
                },
                {
                    'Effect': 'Allow',
                    'Principal': {
                        'AWS': 'arn:aws:iam::386209384616:root'
                    },
                    'Action': 's3:PutObject',
                    'Resource': resource_wildcard
                }
            ]
        }
        bucket_policy = json.dumps(policy_dict)
        try:
            s3_client = boto3.client('s3', **self.credentials)
            s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def _delete_bucket_policy(self, bucket_name):
        """Delete bucket policy.

        :param bucket_name: Bucket to delete policy from.
        :return: True if policy deleted, else False
        """
        try:
            s3_client = boto3.client('s3', **self.credentials)
            s3_client.delete_bucket_policy(Bucket=bucket_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def create_cost_usage_report(self, cost_report, bucket_name, region='us-east-1'):
        """Create a cost usage report in the specified bucket.

        :param cost_report: Name of cost report
        :param bucket_name: Bucket to write cost report to
        :return: True if cost report created, else False
        """

        report_definition = {
            'ReportName': cost_report,
            'TimeUnit': 'HOURLY',
            'Format': 'textORcsv',
            'Compression': 'GZIP',
            'AdditionalSchemaElements': [
                'RESOURCES',
            ],
            'S3Bucket': bucket_name,
            'S3Prefix': '',
            'S3Region': region,
            'AdditionalArtifacts': [
                'REDSHIFT', 'QUICKSIGHT'
            ],
            'RefreshClosedReports': True,
            'ReportVersioning': 'CREATE_NEW_REPORT'
        }
        if not self._set_cur_bucket_policy(bucket_name):
            return False

        try:
            cur_client = boto3.client('cur', **self.credentials)
            cur_client.put_report_definition(ReportDefinition=report_definition)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def list_cost_usage_reports(self):
        """Get a list of cost usage reports.
        
        :return: list of cost usage reports
        """
        reports = []
        try:
            cur_client = boto3.client('cur', **self.credentials)
            cur_paginator = cur_client.get_paginator(operation_name='describe_report_definitions')
            reports = cur_paginator.paginate()
        except ClientError as e:
            logging.error(e)
        return reports

    def delete_cost_usage_report(self, cost_report, bucket_name):
        """Delete an existing cost usage report.

        :param cost_report: Cost report name to delete
        :param bucket_name: Bucket to remove policy from
        :return: True if cost report created, else False
        """
        if not self._delete_bucket_policy(bucket_name):
            return False

        try:
            cur_client = boto3.client('cur', **self.credentials)
            cur_client.delete_report_definition(ReportName=cost_report)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def _create_cost_policy(self, policy_name, bucket_name):
        """Create cost IAM policy.
        
        :param bucket_name: Bucket to share with an external account access
        :return: ARN string
        """
        resource = f'arn:aws:s3:::{bucket_name}'
        resource_wildcard = f'arn:aws:s3:::{bucket_name}/*'
        policy_dict = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'VisualEditor0',
                    'Effect': 'Allow',
                    'Action': [
                        's3:Get*',
                        's3:List*'
                    ],
                    'Resource': [
                        resource,
                        resource_wildcard
                    ]
                },
                {
                    'Sid': 'VisualEditor1',
                    'Effect': 'Allow',
                    'Action': [   
                        'organizations:List*',
                        'organizations:Describe*',
                        's3:ListAllMyBuckets',
                        'iam:ListAccountAliases',
                        's3:HeadBucket',
                        'cur:DescribeReportDefinitions'
                    ],
                    'Resource': '*'
                }
            ]
        }
        try:
            iam_client = boto3.client('iam', **self.credentials)
            response = iam_client.create_policy(PolicyName=policy_name,
                                     PolicyDocument=json.dumps(policy_dict))
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def _create_cost_role(self, role_name, share_account):
        """Create cost role.

        :parma role_name: The name of the role to create  
        :param share_account: Account ID to share cost data with
        :return: ARN string
        """
       
        arn = None
        description = 'Cost Management Reporting Role'
        share_arn = f'arn:aws:iam::{share_account}:root'
        trust_policy = {
			'Version': '2012-10-17',
			'Statement': [{
				'Effect': 'Allow',
				'Principal': {
					'AWS': share_arn
				},
				'Action': 'sts:AssumeRole',
				'Condition': {}
			}]
		}
        try:
            iam_client = boto3.client('iam', **self.credentials)
            response = iam_client.create_role(
                Path='/',
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=description,
                MaxSessionDuration=3600
            )
            arn = response.get('Role', {}).get('Arn')
        except ClientError as e:
            logging.error(e)
        return arn

    def create_cost_arn(self, policy_name, bucket_name, role_name, share_account):
        """Create cost ARN.

        :param policy_name: The name of the policy to create
        :param bucket_name: Bucket to share with an external account access
        :parma role_name: The name of the role to create  
        :param share_account: Account ID to share cost data with
        :return: ARN string
        """
        policy = self._create_cost_policy(policy_name, bucket_name)
        if not policy:
            return None
        arn = self._create_cost_role(role_name, share_account)
        return arn

    def _get_account_id(self):
        """Get the AWS account ID.
        
        :return: Account ID
        """
        account_id  = None
        try:
            sts_client = boto3.client('sts', **self.credentials)
            account_id = sts_client.get_caller_identity()['Account']
        except ClientError as e:
            logging.error(e)
        return account_id

    def get_iam_policy(self, policy_name):
        """Return policy by name.

        :param policy_name: The policy to retrieve
        :return: Policy dictionary
        """
        policy = None
        account_id = self._get_account_id()
        policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
        if not account_id:
            return policy
        try:
            iam_client = boto3.client('iam', **self.credentials)
            policy = iam_client.get_policy(PolicyArn=policy_arn)
        except ClientError as e:
            logging.error(e)
        return policy

    def get_iam_role(self, role_name):
        """Return role by name.

        :param role_name: The role to retrieve
        :return: Role dictionary
        """
        role = None
        try:
            iam_client = boto3.client('iam', **self.credentials)
            role = iam_client.get_role(RoleName=role_name)
        except ClientError as e:
            logging.error(e)
        return role

    def delete_iam_policy(self, policy_name):
        """Delete an IAM policy by name.

        :param policy_name: The Policy to delete
        :return: True if policy deleted, else False
        """
        account_id = self._get_account_id()
        policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
        if not account_id:
            return False

        try:
            iam_client = boto3.client('iam', **self.credentials)
            iam_client.delete_policy(PolicyArn=policy_arn)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_iam_role(self, role_name):
        """Delete an IAM role by name.

        :param role_name: The Role to delete
        :return: True if role deleted, else False
        """
        try:
            iam_client = boto3.client('iam', **self.credentials)
            iam_client.delete_role(RoleName=role_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True