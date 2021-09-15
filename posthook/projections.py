#!/usr/bin/python3

import sys, time, argparse, boto3

# args
parser = argparse.ArgumentParser(description='projections prehook')
parser.add_argument('-c','--cluster', help='cluster name', required=True)
parser.add_argument('-s','--service', help='service name', required=True)
parser.add_argument('-p','--profile', help='profile name', default='')
parser.add_argument('-i','--interval', type=int, help='polling interval for fetching desiredCount in seconds. default: 2', default=2)
args = parser.parse_args()

def setServiceDesiredCount(ecs,count):
    response = ecs.update_service(
        cluster= args.cluster,
        service= args.service,
        desiredCount = count
    )


def main():
    # setup boto client
    if args.profile != '':
        session = boto3.Session(profile_name=args.profile)
        ecs = session.client("ecs")
    else:
        ecs = boto3.client("ecs")

    print("set desired count to 1")

    setServiceDesiredCount(ecs, 1)
    print("posthook executed succesfully")
    sys.exit()

if __name__ == "__main__":
    main()
