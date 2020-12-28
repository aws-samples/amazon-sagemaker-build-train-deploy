import json
import time
import boto3
import logging
import cfnresponse
from botocore.exceptions import ClientError

client = boto3.client('sagemaker')


def lambda_handler(event, context):
    try:
        if event['RequestType'] == 'Create':
            handle_create(event, context)
        elif event['RequestType'] == 'Update':
            handle_update(event, context)
        elif event['RequestType'] == 'Delete':
            handle_delete(event, context)
    except ClientError as exception:
        logging.error(exception)
        cfnresponse.send(event, context, cfnresponse.FAILED,
                         {}, error=str(exception))


def handle_create(event, context):
    print("**Starting running the SageMaker workshop setup code")
    resource_config = event['ResourceProperties']

    print("**Creating studio domain")
    response_data = create_studio_domain(resource_config)
    cfnresponse.send(event, context, cfnresponse.SUCCESS,
                     {'DomainId': response_data['DomainId']}, physicalResourceId=response_data['DomainId'])


def handle_delete(event, context):
    print('Received delete event')
    domain_id = event['PhysicalResourceId']
    try:
        client.describe_domain(DomainId=domain_id)
    except ClientError as exception:
        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         {}, physicalResourceId=event['PhysicalResourceId'])
        return
    delete_domain(domain_id)
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                     physicalResourceId=event['PhysicalResourceId'])


def handle_update(event, context):
    logging.info('Received Update event')
    domain_id = event['PhysicalResourceId']
    default_user_settings = event['ResourceProperties']['DefaultUserSettings']
    update_domain(domain_id, default_user_settings)
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {'DomainId' : domain_id},
                     physicalResourceId=event['PhysicalResourceId'])


def create_studio_domain(config):
    vpc = boto3.client('ec2')
    vpc_id = vpc.describe_vpcs()['Vpcs'][0]['VpcId']
    subnet_list = vpc.describe_subnets()['Subnets']
    subnet_ids = [subnet['SubnetId'] for subnet in subnet_list]
    default_user_settings = config['DefaultUserSettings']
    domain_name = config['DomainName']

    response = client.create_domain(
        DomainName=domain_name,
        AuthMode='IAM',
        DefaultUserSettings=default_user_settings,
        SubnetIds=subnet_ids,
        VpcId=vpc_id
    )

    domain_id = response['DomainArn'].split('/')[-1]
    created = False
    while not created:
        response = client.describe_domain(DomainId=domain_id)
        time.sleep(5)
        if response['Status'] == 'InService':
            created = True

    logging.info("**SageMaker domain created successfully: %s", domain_id)
    return response


def delete_domain(domain_id):
    response = client.delete_domain(
        DomainId=domain_id,
        RetentionPolicy={
            'HomeEfsFileSystem': 'Delete'
        }
    )
    deleted = False
    while not deleted:
        try:
            client.describe_domain(DomainId=domain_id)
        except ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFound':
                print('Deleted')
                deleted = True
                return
        time.sleep(5)
    return response


def update_domain(domain_id, default_user_settings):
    response = client.update_domain(
        DomainId=domain_id,
        DefaultUserSettings=default_user_settings
    )
    updated = False
    while not updated:
        response = client.describe_domain(DomainId=domain_id)
        if response['Status'] == 'InService':
            updated = True
        else:
            logging.info('Updating .. %s', response['Status'])
        time.sleep(5)
    return response
