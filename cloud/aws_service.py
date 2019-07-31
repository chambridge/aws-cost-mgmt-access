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
            self.credentials = None
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
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = boto3.client('s3', region_name=region)
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
            s3_client = boto3.client('s3')
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
            s3_client = boto3.client('s3')
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
            s3_client = boto3.client('s3')
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
            cur_client = boto3.client('cur')
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
            cur_client = boto3.client('cur')
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
            cur_client = boto3.client('cur')
            cur_client.delete_report_definition(ReportName=cost_report)
        except ClientError as e:
            logging.error(e)
            return False
        return True