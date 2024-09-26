#!/usr/bin/python

import os, sys, subprocess, json, time, argparse

# args
parser = argparse.ArgumentParser(description='awscurl polling action')
parser.add_argument('-e','--environment', help='options ["test", "beta", "tni", "stg", "acc", "prd"]', required=True)
parser.add_argument('-v','--version', help='deploy version', required=True)
parser.add_argument('-s','--status_url', required=True)
parser.add_argument('-d', '--deploy_url', required=True)
parser.add_argument('--access_key', help='aws access key', required=True)
parser.add_argument('--secret_key', help='aws secret key', required=True)
parser.add_argument('-r','--region', help='region default: eu-west-1', default='eu-west-1')
parser.add_argument('-i','--interval', type=int, help='polling interval in seconds. default: 2', default=2)
parser.add_argument('-t','--deploy_target', help='options ["none", "beanstalk", "ecs", "ecs_service", "agb_ecs_service", "ecs_scheduled_task"]', default='none', required=False)
parser.add_argument('--domain', help='options ["none", "basisregisters"]', default='none', required=False)
parser.add_argument('--project', help='options ["none", "basisregisters"]', default='none', required=False)
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

def exec(cmd):
    return (subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             universal_newlines=True).communicate()[0]).strip()

def sendBuildRequest():
    payload = {
        "deploy_target": str(args.deploy_target),
        "version":{str(args.project): str(args.version)}
    }

    aws_deploy_req_body = json.dumps(payload)
    sendGroupedOutput("request body",[aws_deploy_req_body]) #Logging
    cmd = f"awscurl --access_key '{args.access_key}' --secret_key '{args.secret_key}' --region '{args.region}' --service execute-api -X POST -d '{aws_deploy_req_body}' {args.deploy_url}"

    output = exec(cmd)
    sendGroupedOutput("deploy response",[output]) #Logging
    return json.loads(output)

def getStatus(build_id):
    aws_status_url = f'{args.status_url}/{build_id}'
    cmd = f"awscurl --access_key '{args.access_key}' --secret_key '{args.secret_key}' --region '{args.region}' --service execute-api {aws_status_url}"
    output = exec(cmd)
    status_responses.append(output)
    return json.loads(output)

def main():
    print(f'Start')

    buildResponse = sendBuildRequest()
    
    if buildResponse.get('body') is None:
        sendFailed("deploy response", "Something went wrong")
        return
    
    sendOutput("build-uuid", buildResponse['body']['BuildUuid'])
    time.sleep(10)
    while True:
        try:
            statusResponse = getStatus(buildResponse['body']['BuildUuid'])
            status = statusResponse['status']
            print(f'Deployment for version {args.version} to environment {args.environment}: {status}"')
        except:
            print(f'Polling request failed. Trying again!')
            continue
        
        if status == 'SUCCEEDED':
           break

        if status == 'INPROGRESS' or status == 'STOPPING':
           time.sleep(args.interval)
           continue
        
        sendGroupedOutput("status responses",status_responses)
        sendWarning(f"build-uuid: {statusResponse }")
        sendFailed(f'Deployment for version {args.version} to environment {args.environment}: {status}')
    
    sendGroupedOutput("status responses",  [status_responses])
    sendOutput("status", status)
    sendOutput("final-message",f'Deployment for version {args.version} to environment {args.environment}: {status}')
    sys.exit()

if __name__ == "__main__":
    main()
