#!/usr/bin/python

import os, sys, subprocess, time, argparse

# args
parser = argparse.ArgumentParser(description='projections prehook')
parser.add_argument('-c','--cluster', help='cluster name', required=True)
parser.add_argument('-s','--service', help='service name', required=True)
parser.add_argument('-p','--profile', help='profile name', default='')
parser.add_argument('-i','--interval', type=int, help='polling interval for fetching desiredCount in seconds. default: 2', default=2)
args = parser.parse_args()

def exec(cmd):
    output = subprocess.Popen(cmd,
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True).communicate()
    if output[1] != '':
        print(cmd)
        print(output[1].strip())
        sys.exit(-1)
    return output[0].strip()

def getProfile():
    if args.profile != '':
        return f" --profile {args.profile}"
    return ''


def setServiceDesiredCount(count):
    cmd = f"aws ecs update-service --cluster {args.cluster} --service {args.service}{getProfile()} --desired-count {count}"
    output = exec(cmd)
    print(f"update desired count: {output}")
    if "An error occurred" in output:
        print(f"update service failed: {output}")
        sys.exit(-1)

def getServiceDesireCount():
    cmd = f"aws ecs describe-services --cluster {args.cluster} --service {args.service}{getProfile()} | jq '.services[0].deployments[0].desiredCount'"
    output = exec(cmd)
    print(f"current desired count: {output}")
    return int(output)


def main():
    desiredCount = getServiceDesireCount()        
    # upscale to 1
    if desiredCount == 0:
        print(f'set desired count to 1')
        setServiceDesiredCount(0)
        time.sleep(args.interval)
    
    # wait till complete
    while True:
        desiredCount = getServiceDesireCount()
        if desiredCount != 0:
            print(f'current desired count is {desiredCount}')
            break
    print(f'posthook executed succesfully')
    sys.exit()

if __name__ == "__main__":
    main()
