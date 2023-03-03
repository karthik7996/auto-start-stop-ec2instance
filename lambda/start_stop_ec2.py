import boto3
import os
import logging
import json
import urllib3

slack_url = os.environ['slack_url']
teams_url = os.environ['teams_url']



def lambda_handler(event, context):
    operation = event['Operation']
    print('Running ' + operation + ' for EC2')
    # Start/Stop EC2 Instances
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name':'tag:start_stop_tagname',
                'Values':['enable']
            }
        ]
    )
    #print('Checking EC2 instances')
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            print('Checking EC2 instance ' + instance['InstanceId'])
            if 'Tags' in instance and len(instance['Tags']):
                for tag in instance['Tags']:
                    if tag['Key'] == 'aws:autoscaling:groupName':
                            process_asg(operation,instance['InstanceId'],tag['Value'])
            if operation == 'Start':
                print('Starting EC2 instance ' + instance['InstanceId'])
                Instnce_id = instance['InstanceId']
                try:
                    ec2_client.start_instances(InstanceIds=[instance['InstanceId']])
                    message = "Ec2 instances Started."+"\n" +"InstanceIds: " + str(Instnce_id)
                except Exception as e:
                    print('EC2 instance ' + instance['InstanceId'] + ' failed to start:')
                    print(e)
            else:
                print('Stopping EC2 instance ' + instance['InstanceId'])
                Instnce_id = instance['InstanceId']
                try:
                    ec2_client.stop_instances(InstanceIds=[instance['InstanceId']])
                    message = "Ec2 instances Stopped."+"\n"+ "InstanceIds: " + str(Instnce_id)
                except Exception as e:
                    print('EC2 instance ' + instance['InstanceId'] + ' failed to stop:')
                    print(e) 
            post_to_slack(message)
           
           
                    
def post_to_slack(message):
    webhook_url = slack_url
    teams_webhook_url = teams_url
    slack_data = {'text': message}
    http = urllib3.PoolManager()
    headers={'Content-Type': 'application/json'}
    encoded_data = json.dumps(slack_data).encode('utf-8')
    response = http.request('POST',webhook_url,body=encoded_data,headers=headers)
    response1 = http.request('POST',teams_webhook_url,body=encoded_data,headers=headers)
    return True