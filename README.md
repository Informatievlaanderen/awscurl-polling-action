# awscurl-polling-action
A Github action which uses awscurl to poll an AWS endpoint

## Example
```yaml
name: Sample
on:
  workflow_dispatch
jobs:
  one:
      runs-on: ubuntu-latest
      steps:
        - name: awscurl-polling-action
          id: awscurl-polling-action
          uses: informatievlaanderen/awscurl-polling-action@main
          with:
            environment: stg
            version: ${{ secrets.VERSION }}
            status-url: ${{ secrets.STATUS_URL }}
            deploy-url: ${{ secrets.DEPLOY_URL }}
            access-key: ${{ secrets.ACCESS_KEY }}
            secret-key: ${{ secrets.SECRET_KEY }}
            interval: 2
            deploy-target: 'none'
            domain: 'none'
            project: 'none'
        - name: output
          shell: bash
          run: |
            echo build-uuid: ${{ steps.awscurl-polling-action.outputs.build-uuid }}
            echo Status: ${{ steps.awscurl-polling-action.outputs.status }}
            echo ${{ steps.awscurl-polling-action.outputs.final-message }}
```

### Inputs

|Argument| Description | Default | Required |
|--------|-------------|---------|----------|
| environment | The environment in which it should be deployed e.g. `test`, `beta`, `tni`, `stg`, `prd` | `stg` | Yes |
| version | The release version. | - | Yes |
| status-url | The status url for fetching the deploy status | - | Yes |
| deploy-url | The deploy url for sending a request for deployment | - | Yes |
| access-key | AWS Access Key | - | Yes |
| secret-key | AWS Secret Key | - | Yes |
| interval | Polling interval in seconds | 2 | No |
| deploy-target | `none`, `beanstalk`, `ecs`, `ecs_service`, `agb_ecs_service`, `ecs_scheduled_task` | `none` | No |
| domain | `none`, `basisregisters` | `none` | No |
| project | `none`, `basisregisters` | `none` | No |

### Outputs
|Argument| Description |
|--------|-------------|
| build-uuid | Identifier |
| status | Final build status |
| final-message | extra info about the build |
