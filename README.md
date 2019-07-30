# aws-cost-mgmt-access
Proof of concept code to setup an cost mgmt data extraction and pull data file. 

## Background
The sample code here is meant to setup cost usage reports as described in this [AWS document](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-reports.html) using an IAM user.

## Getting Started

1. Clone the repository:
```
git clone https://github.com/chambridge/aws-cost-mgmt-access.git
```

2. Setup virtual environment with _pipenv_
```
cd aws-cost-mgmt-access
pipenv install
```

3. Create an IAM user
Follow the steps in the following AWS document to [create an IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html

Add the following role to the IAM user: _PowerUser_.


4. Set environment variables
Copy the `.env.example` file to `.env` and provide the necessary variables.
```
cp ./.env.example ./.env
```

5. Enter virtual environment shell with set environment variables
```
pipenv shell
```

## Code Structure

Currently, the code to interact with AWS resides in the `cloud` directory. Outside of this there are several single purpose scripts to work with s3 buckets, and cost and usage reports. These scripts can be called directedly as seen in the following example:

```
python setup_s3_bucket.py
