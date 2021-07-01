#!/usr/bin/python

import sys, subprocess, json, time, argparse

# args
parser = argparse.ArgumentParser(description='awscurl polling action')
parser.add_argument('-e','--environment', help='options ["test", "beta", "tni", "stg", "prd"]', required=True)
parser.add_argument('-v','--version', help='deploy version', required=True)
parser.add_argument('-s','--status_url', required=True)
parser.add_argument('-d', '--deploy_url', required=True)
parser.add_argument('--access_key', help='aws access key', required=True)
parser.add_argument('--secret_key', help='aws secret key', required=True)
parser.add_argument('-r','--region', help='region default: eu-west-1', default='eu-west-1')
parser.add_argument('-i','--interval', type=int, help='polling interval in seconds. default: 2', default=2)
args = parser.parse_args()

def exec(cmd):
    return (subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             universal_newlines=True).communicate()[0]).strip()

def sendBuildRequest():
    aws_deploy_req_body = '{\"environment\":\"' + args.environment + '\",\"version\":\"' + args.version + '\"}'
    cmd = f"awscurl --access_key '{args.access_key}' --secret_key '{args.secret_key}' --region '{args.region}' --service execute-api -X POST -d '{aws_deploy_req_body}' {args.deploy_url}"
    output = exec(cmd)
    print(f'deploy response: {output}')
    return json.loads(output)

def getStatus(build_id):
    aws_status_url = f'{args.status_url}/{build_id}'
    cmd = f"awscurl --access_key '{args.access_key}' --secret_key '{args.secret_key}' --region '{args.region}' --service execute-api '{aws_status_url}'"
    output = exec(cmd)
    print(f'status response: {output}')
    return json.loads(output)

def main():
    buildResponse = sendBuildRequest()
    time.sleep(10)
    while True:
        statusResponse = getStatus(buildResponse['body']['BuildUuid'])
        status = statusResponse['status']
        print(f'Deployment for version {args.version} to environment {args.environment}: {status}"')

        if status == 'SUCCEEDED':
            break

        if status == 'INPROGRESS' or status == 'STOPPING':
            time.sleep(args.interval)
            continue

        print(f'Deployment for version {args.version} to environment {args.environment}: {status}"')
        sys.exit(1)
    sys.exit()

if __name__ == "__main__":
    main()
