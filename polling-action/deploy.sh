#!/bin/sh
VERSION=`cat VERSION | tr -d " \t\n\r"`

# Remove excisting containers with same version
docker image rm -f ghcr.io/informatievlaanderen/awscurl-polling-action:$VERSION

# Build containers
docker build -t ghcr.io/informatievlaanderen/awscurl-polling-action:$VERSION    -f ./Dockerfile .

# Push containers to registry
docker push ghcr.io/informatievlaanderen/awscurl-polling-action:$VERSION