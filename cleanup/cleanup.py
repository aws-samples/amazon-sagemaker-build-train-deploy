# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import sys
import argparse
import time
import botocore

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sagemaker-studio-domain')

    return parser.parse_args()

def get_efs_volumes():
    efs_client = boto3.client("efs")
    response = efs_client.describe_file_systems()
    return response["FileSystems"]

def find_efs_volume_managed_by_sagemaker_domain(domain_arn):
    efs_volumes = get_efs_volumes()
    for volume in efs_volumes:
        for tag in volume["Tags"]:
            if (tag.get("Key") == "ManagedByAmazonSageMakerResource") and (tag.get("Value") == domain_arn):
                return volume
    return None

def delete_mount_targets_for_file_system(file_system_id):
    efs_client = boto3.client("efs")
    mount_targets = efs_client.describe_mount_targets(FileSystemId=file_system_id)["MountTargets"]

    for mount_target in mount_targets:
        efs_client.delete_mount_target(MountTargetId=mount_target["MountTargetId"])
        print(f"Deleted mount target {mount_target['MountTargetId']} for the EFS volume.")

def list_security_groups_managed_by_sagemaker_domain(domain_arn):
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_security_groups(Filters=[
                {
                    'Name': 'tag:ManagedByAmazonSageMakerResource',
                    'Values': [
                        domain_arn
                    ]
                }])
    return response["SecurityGroups"]

def delete_security_groups(security_groups):
    ec2 = boto3.resource("ec2")
    for security_group in security_groups:
        sg = ec2.SecurityGroup(security_group["GroupId"])
        if sg.ip_permissions:
            sg.revoke_ingress(IpPermissions=sg.ip_permissions)
            print(f"Removed ingress permissions on security group {security_group['GroupId']}")     
        if sg.ip_permissions_egress:
            sg.revoke_egress(IpPermissions=sg.ip_permissions_egress)
            print(f"Removed egress permissions on security group {security_group['GroupId']}")     

    ec2_client = boto3.client("ec2")
    for security_group in security_groups:
        print(f"Deleting security group {security_group['GroupId']}...")
        run_with_retry(lambda: ec2_client.delete_security_group(GroupId=security_group["GroupId"]), "DependencyViolation")
        print(f"Deleted security group {security_group['GroupId']}")   

def run_with_retry(target, expected_error_message):
    attempt = 1
    while True:
        try:
            target() 
            break
        except Exception as ex:
            if not isinstance(ex, botocore.exceptions.ClientError) or f"({expected_error_message})" not in str(ex):
                raise ex
            if attempt > 7:
                raise ex
            
            wait_time = pow(2, attempt)
            print(f"Dependent objects still exist. Retrying after {wait_time} seconds...")
            time.sleep(wait_time)  
            attempt += 1

def list_sagemaker_endpoint_eni(vpc_id):
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_network_interfaces(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        }])
    return list(filter(lambda eni: ":SageMaker" in eni["RequesterId"], response["NetworkInterfaces"]))

def delete_eni(eni_list):
    ec2_client = boto3.client("ec2")
    for eni in eni_list:
        if "Attachment" in eni:
            attachment_id = eni["Attachment"]["AttachmentId"]
            print(f"Detaching SageMaker endpoint ENI attachment {attachment_id}...")
            ec2_client.detach_network_interface(AttachmentId=attachment_id, Force=True)
        
        eni_id = eni['NetworkInterfaceId']
        print(f"Deleting SageMaker endpoint ENI {eni_id}...")
        run_with_retry(lambda: ec2_client.delete_network_interface(NetworkInterfaceId=eni_id), "InvalidParameterValue")
        print(f"Deleted SageMaker endpoint ENI {eni_id}")

    
def main():
    args = parse_args()

    security_groups = list_security_groups_managed_by_sagemaker_domain(args.sagemaker_studio_domain)
    vpc_id = security_groups[0]["VpcId"]
    network_interfaces = list_sagemaker_endpoint_eni(vpc_id)
    
    delete_eni(network_interfaces)

    efs_volume_managed_by_sagemaker_domain = find_efs_volume_managed_by_sagemaker_domain(args.sagemaker_studio_domain)
    if efs_volume_managed_by_sagemaker_domain is None:
        raise Exception(f"Could not find the EFS volume managed by Amazon SageMaker domain {args.sagemaker_studio_domain}")
    print(f"Found EFS Volume managed by SageMaker domain {args.sagemaker_studio_domain}. FileSystemId is: {efs_volume_managed_by_sagemaker_domain['FileSystemId']}\n")
    
    delete_mount_targets_for_file_system(efs_volume_managed_by_sagemaker_domain["FileSystemId"])
    
    delete_security_groups(security_groups)

    print(f"If you don't need the data in the EFS volume {efs_volume_managed_by_sagemaker_domain['FileSystemId']} created by SageMaker, delete it from the AWS Console.")
    
if __name__ == '__main__':
    main()