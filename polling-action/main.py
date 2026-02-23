#!/usr/bin/python

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

import boto3
import botocore
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

# args
parser = argparse.ArgumentParser(description='awscurl polling action')
parser.add_argument('-e','--environment', help='options ["test", "beta", "tni", "stg", "acc", "prd"]', required=True)
parser.add_argument('-v','--version', help='deploy version', required=True)
parser.add_argument('-s','--status_url', required=True)
parser.add_argument('-d', '--deploy_url', required=True)
parser.add_argument('--role_arn', help='aws role arn to assume for credentials', required=True)
parser.add_argument('-r','--region', help='region default: eu-west-1', default='eu-west-1')
parser.add_argument('-i','--interval', type=int, help='polling interval in seconds. default: 2', default=2)
parser.add_argument('-t','--deploy_target', help='options ["none", "beanstalk", "ecs", "ecs_service", "agb_ecs_service", "ecs_scheduled_task"]', default='none', required=False)
parser.add_argument('--domain', help='options ["none", "basisregisters"]', default='none', required=False)
parser.add_argument('--project', help='options ["none", "basisregisters"]', default='none', required=False)
parser.add_argument('--application', help='options ["none", "basisregisters"]', default='none', required=True)
parser.add_argument('--use_subfolder', type=bool, help='options [true, false] | default: false', default=False, required=False)
args = parser.parse_args()

status_responses = []

def sendWarning(message):
    print(f'::warning::{message}')

def sendFailed(message):
    print(f'::error::{message}')
    sys.exit(1)

def sendGroupedOutput(group_name, body):
    print(f'::group::{group_name}')
    for line in body:
        print(f'{line}')
    print(f'::endgroup::')

def sendOutput(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'{name}={value}', file=fh)

def get_github_oidc_token():
    request_url = os.getenv('ACTIONS_ID_TOKEN_REQUEST_URL')
    request_token = os.getenv('ACTIONS_ID_TOKEN_REQUEST_TOKEN')

    if not request_url or not request_token:
        return None

    separator = '&' if '?' in request_url else '?'
    token_url = f'{request_url}{separator}audience=sts.amazonaws.com'
    request = urllib.request.Request(token_url)
    request.add_header('Authorization', f'bearer {request_token}')

    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode('utf-8'))

    return payload.get('value')

def get_credentials():
    role_arn = args.role_arn.strip()
    if not role_arn:
        sendFailed('role_arn is required')

    base_session = boto3.Session(region_name=args.region)
    sts_client = base_session.client('sts', region_name=args.region)

    try:
        assume_role_response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='awscurl-polling-action'
        )
    except botocore.exceptions.NoCredentialsError:
        oidc_token = get_github_oidc_token()
        if not oidc_token:
            sendFailed(
                'Unable to locate AWS credentials. '
                'Provide base AWS credentials (for sts:AssumeRole) '
                'or enable GitHub OIDC (permissions: id-token: write).'
            )

        assume_role_response = sts_client.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName='awscurl-polling-action',
            WebIdentityToken=oidc_token
        )

    assumed = assume_role_response['Credentials']
    print(f'::debug::Using assumed role credentials for role: {role_arn}')
    return Credentials(
        access_key=assumed['AccessKeyId'],
        secret_key=assumed['SecretAccessKey'],
        token=assumed['SessionToken']
    )

def signed_post(url, credentials, payload=None):
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['content-type'] = 'application/json'

    aws_request = AWSRequest(method='POST', url=url, data=data, headers=headers)
    SigV4Auth(credentials, 'execute-api', args.region).add_auth(aws_request)
    prepared = aws_request.prepare()

    request = urllib.request.Request(url=url, data=data, method='POST')
    for header_name, header_value in prepared.headers.items():
        request.add_header(header_name, header_value)

    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as error:
        error_body = error.read().decode('utf-8', errors='replace')
        sendGroupedOutput('request error', [f'HTTP {error.code}', error_body])
        raise

def sendBuildRequest(credentials):
    payload = {
        "deploy_target": str(args.deploy_target),
        "version":{str(args.application): str(args.version)}
    }

    if str(args.domain) != "none" and args.use_subfolder:
        payload["application_subfolder"] = str(args.domain)

    sendGroupedOutput("request body", [json.dumps(payload)])
    print(f'::debug::Deploying with v4!')
    output = signed_post(args.deploy_url, credentials, payload)
    sendGroupedOutput("deploy response",[output]) #Logging
    return json.loads(output)

def getStatus(build_id, credentials):
    aws_status_url = f'{args.status_url}/{build_id}'
    output = signed_post(aws_status_url, credentials)
    status_responses.append(output)
    return json.loads(output)

def main():
    print(f'::debug::Start')

    credentials = get_credentials()
    buildResponse = sendBuildRequest(credentials)

    sendOutput("build-uuid", buildResponse['BuildUuid'])
    time.sleep(10)
    while True:
        try:
            statusResponse = getStatus(buildResponse['BuildUuid'], credentials)
            statusMessage = statusResponse['message']
            print(f'::debug::Message: "{statusMessage}"')
            status = statusResponse['details']['status']
            print(f'::debug::Deployment for version {args.version} to environment {args.environment}: "{status}"')
        except Exception as e:
            print(f'::debug::Polling request failed with exception: {e}. Trying again!')
            continue
        
        if statusMessage == 'Succeeded':
           break

        if statusMessage == 'InProgress' or statusMessage == 'Stopping':
           time.sleep(args.interval)
           continue
        
        sendGroupedOutput("status responses",status_responses)
        sendWarning(f"build-uuid: {statusResponse }")
        sendFailed(f'Deployment for version {args.version} to environment {args.environment}: {statusMessage}')
    
    sendGroupedOutput("status responses", status_responses)
    sendOutput("status", statusMessage)
    sendOutput("final-message",f'Deployment for version {args.version} to environment {args.environment}: {status}')
    sys.exit()

if __name__ == "__main__":
    main()
