# awscurl-polling-action
A Github action which uses awscurl to poll an AWS endpoint

## Inputs

## `environment`
**Required** The environment in which it should be deployed 
options: `test`, `beta`, `tni`, `stg`, `prd` 
default `stg`.

## `version`
**Required** The release version.

## `status-url`
**Required** The status url for fetching the deploy status

## `deploy-url`
**Required** The deploy url for sending a request for deployment

## `access-key`
**Required** AWS access key

## `secret-key`
**Required** AWS secret key

## `region`
**Optional** AWS region 
default: `eu-west-1`

## `interval`
**Optional** Polling interval in seconds
default: `2`


## Example usage
```
uses: informatievlaanderen/awscurl-polling-action@main
with:
    environment: stg
    version: ${{ secrets.VERSION }}
    status-url: ${{ secrets.STATUS_URL }}
    deploy-url: ${{ secrets.DEPLOY_URL }}
    access-key: ${{ secrets.ACCESS_KEY }}
    secret-key: ${{ secrets.SECRET_KEY }}
    region: eu-west-1
    interval: 2
```