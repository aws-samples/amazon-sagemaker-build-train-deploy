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
    response_data = create_user_profile(resource_config)
    cfnresponse.send(event, context, cfnresponse.SUCCESS,
                     {'UserProfileName': response_data['UserProfileName']}, physicalResourceId=response_data['UserProfileName'])


def handle_delete(event, context):
    print('Received delete event')
    user_profile_name = event['PhysicalResourceId']
    domain_id = event['ResourceProperties']['DomainId']
    try:
        client.describe_user_profile(DomainId=domain_id, UserProfileName=user_profile_name)
    except ClientError as exception:
        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         {}, physicalResourceId=event['PhysicalResourceId'])
        return
    delete_user_profile(domain_id, user_profile_name)
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                     physicalResourceId=event['PhysicalResourceId'])


def handle_update(event, context):
    logging.info('Received Update event')
    user_profile_name = event['PhysicalResourceId']
    domain_id = event['ResourceProperties']['DomainId']
    user_settings = event['ResourceProperties']['UserSettings']
    update_user_profile(domain_id, user_profile_name, user_settings)
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                     physicalResourceId=event['PhysicalResourceId'])


def create_user_profile(config):
    domain_id = config['DomainId']
    user_profile_name = config['UserProfileName']
    user_settings = config['UserSettings']

    response = client.create_user_profile(
        DomainId=domain_id,
        UserProfileName=user_profile_name,
        UserSettings=user_settings,
    )

    created = False
    while not created:
        response = client.describe_user_profile(DomainId=domain_id, UserProfileName=user_profile_name)
        time.sleep(5)
        if response['Status'] == 'InService':
            created = True

    logging.info("**SageMaker domain created successfully: %s", domain_id)
    return response


def delete_user_profile(domain_id, user_profile_name):
    response = client.delete_user_profile(
        DomainId=domain_id,
        UserProfileName=user_profile_name
    )
    deleted = False
    while not deleted:
        try:
            client.describe_user_profile(DomainId=domain_id, UserProfileName=user_profile_name)
        except ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFound':
                print('Deleted')
                deleted = True
                return
        time.sleep(5)
    return response


def update_user_profile(domain_id, user_profile_name, user_settings):
    response = client.update_user_profile(
        DomainId=domain_id,
        UserProfileName=user_profile_name,
        UserSettings=user_settings
    )
    updated = False
    while not updated:
        response = client.describe_user_profile(DomainId=domain_id,UserProfileName=user_profile_name)
        if response['Status'] == 'InService':
            updated = True
        else:
            logging.info('Updating .. %s', response['Status'])
        time.sleep(5)
    return response
