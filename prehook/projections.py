#!/usr/bin/python3

from os import system
import sys, time, argparse, boto3

# args
parser = argparse.ArgumentParser(description='projections prehook')
parser.add_argument('-c','--cluster', help='cluster name', required=True)
parser.add_argument('-s','--service', help='service name', required=True)
parser.add_argument('-a','--appname', help='projections name e.g.streetname-registry-projections', required=True)
parser.add_argument('-p','--profile', help='profile name', default='')
parser.add_argument('-i','--interval', type=int, help='polling interval for fetching desiredCount in seconds. default: 2', default=2)
args = parser.parse_args()

def getDistributionLockName(ecs):
    # Get task definition name
    taskDefinitions = ecs.list_task_definitions(
        familyPrefix= args.appname,
        status='ACTIVE',
        sort='DESC',
    )
    taskDefinitionName = taskDefinitions["taskDefinitionArns"][0]

    # Get distribution lock names
    description = ecs.describe_task_definition(
        taskDefinition= taskDefinitionName
    )

    # Distributedlocks
    distributedLocks = set()
    for containers in description["taskDefinition"]["containerDefinitions"]:
        an_iterator = filter(lambda env : env["name"] == "DistributedLock__TableName", containers["environment"])
        for i in list(an_iterator):
            distributedLocks.add(i["value"])
    
    print(distributedLocks)
    
    return list(distributedLocks)    

def setServiceDesiredCount(ecs,count):
    response = ecs.update_service(
        cluster= args.cluster,
        service= args.service,
        desiredCount = count
    )

def isDownScaled(ecs):
    response = ecs.describe_services(
        cluster = args.cluster,
        services=[
            args.service,
        ]
    )
    runningCount = response["services"][0]["runningCount"]
    pendingCount = response["services"][0]["pendingCount"]
    return runningCount == 0 and pendingCount == 0

def deleteLockDynomoDb(ecs, dynamodb):
    locks = getDistributionLockName(ecs)
    for lock in locks:
        print(f'deleting table: {lock}')
        response = dynamodb.delete_table(
            TableName = lock
        )
        print(f'deleted table: {lock}')

def main():
    # setup boto client
    if args.profile != '':
        session = boto3.Session(profile_name=args.profile)
        ecs = session.client("ecs")
        dynamodb = session.client("dynamodb")
    else:
        ecs = boto3.client("ecs")
        dynamodb = boto3.client("dynamodb")

    # downscale to 0
    if not isDownScaled(ecs):
        print("set desired count to 0")
        setServiceDesiredCount(ecs, 0)

    # wait till complete
    while not isDownScaled(ecs):
        print("wait")
        time.sleep(args.interval)
    print("service is downscaled")
    
    # delete lock
    deleteLockDynomoDb(ecs, dynamodb)
    print("prehook executed succesfully")

    sys.exit()

if __name__ == "__main__":
    main()
