import boto3
import json
import io
import argparse
from botocore.exceptions import ClientError

def set_boto_profile(profile_name):
    boto3.setup_default_session(profile_name=profile_name)

def get_sqs_queues(client):
    """Retrieve all SQS queues in a given region"""
    try:
        response = client.list_queues()
        return response.get('QueueUrls', [])
    except ClientError as e:
        print("Error listing SQS queues with error: {}".format(e))
        return []

def get_queue_policy(client, queue_url):
    """Retrieve the policy for a given SQS queue"""
    try:
        attributes = client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['Policy'])
        policy = attributes.get('Attributes', {}).get('Policy', '{}')
        return json.loads(policy)
    except ClientError as e:
        print("Error retrieving SQS policy for queue {} with error: {}".format(queue_url,e))
        return {}

def update_queue_policy(client, queue_url, policy):
    """Update the policy for a given SQS queue"""
    try:
        client.set_queue_attributes(QueueUrl=queue_url, Attributes={'Policy': json.dumps(policy)})
        print("Updated policy for queue {}".format(queue_url))
    except ClientError as e:
        print("Error updating policy for queue {} with error: {}".format(queue_url,e))

def check_and_modify_policy(account_id, client, queue_url, mode, sqs_to_log_list):
    """Check SQS policy for external principals and modify if necessary"""
    policy = get_queue_policy(client, queue_url)

    if not policy:
        return

    # Flag to check if policy was modified
    policy_modified = False

    for statement in policy.get('Statement', []):
        # print("Statement: {}".format(statement))
        if 'Principal' in statement:
            # print("Principal: {}".format(statement['Principal']))
            for principal_type, principal_values in statement['Principal'].items():
                # print("Principal values: {}".format(principal_values))
                values = principal_values if isinstance(principal_values, list) else [principal_values]
                for item in values:
                    if principal_type == 'AWS' and account_id not in item:
                        print("External principal found in queue: {}".format(queue_url))
                        sqs_to_log_list.append(queue_url)
                        if mode == 'run':
                            # Modify the principal to only allow access to the specified account
                            statement['Principal'] = {'AWS': account_id}
                            policy_modified = True
                            break

    if policy_modified and mode == 'run':
        # Update the queue policy if modified
        update_queue_policy(client, queue_url, policy)

def get_bucket_region(bucket_name):
    """Retrieve the region where the bucket is located"""
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        region = response['LocationConstraint']
        if region is None:  # If the bucket is in the "us-east-1" region, the region will be None
            region = 'us-east-1'
        return region
    except ClientError as e:
        print(f"Error getting bucket location: {e}")
        return None

def upload_log_to_s3(bucket_name, sqs_to_log_list):
    """Upload the log file to the specified S3 bucket"""
    log_content = "\n".join(sqs_to_log_list)
    log_file = io.BytesIO(log_content.encode('utf-8'))
    print("Log file content: {}".format(log_content))
    
    bucket_region = get_bucket_region(bucket_name)
    if not bucket_region:
        print("Failed to determine bucket region. Aborting upload")
        return
    s3_client = boto3.client('s3', region_name=bucket_region)
    
    try:
        s3_client.upload_fileobj(log_file, bucket_name, 'sqs_names_log.txt')
        print("Log file uploaded to path: {}/sqs_names_log.txt".format(bucket_name))
    except ClientError as e:
        print("Error uploading log file to S3 with error: {}".format(e))

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-aid', '--account_id', required=True, help='The AWS account')
    parser.add_argument('-rta', '--role_to_assume', required=True, help='The AWS role to assume')
    parser.add_argument('-dbt', '--destination_bucket', required=True, help='The destination bucket to write logs')
    parser.add_argument('-md',"--mode", required=True, choices=['log', 'run'], help='Run mode')

    account_id = parser.parse_args().account_id
    role_arn = parser.parse_args().role_to_assume
    destination_bucket = parser.parse_args().destination_bucket
    mode = parser.parse_args().mode

    sqs_to_log_list = []
    
    set_boto_profile(profile_name=role_arn)
    regions = [region['RegionName'] for region in boto3.client('ec2','us-east-1').describe_regions()['Regions']]
    for region in regions:
        print("Checking SQS queues in region: {}".format(region))
        sqs_client = boto3.client('sqs', region_name=region)
        queues = get_sqs_queues(sqs_client)
        print("SQS queues that were found: {} \nin region: {}".format(queues,region))
        
        for queue_url in queues:
            check_and_modify_policy(account_id, sqs_client, queue_url, mode, sqs_to_log_list)

    # Upload log file with problematic SQS queues to S3 if the list is not empty
    if sqs_to_log_list:
        print("Queues that were found with external principals are: {}".format(sqs_to_log_list))
        upload_log_to_s3(destination_bucket, sqs_to_log_list)
    else:
        print("No queues were found with external principals")