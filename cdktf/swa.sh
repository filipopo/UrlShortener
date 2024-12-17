#!/bin/sh

DOCKER_IMAGE=${DOCKER_IMAGE:-filipmania/urlshortener:latest}
docker pull $DOCKER_IMAGE

docker create --name url-temp $DOCKER_IMAGE
docker cp url-temp:/opt/prod_static ./prod_static
docker rm url-temp

touch prod_static/index.html
SWA_CLI_DEPLOYMENT_TOKEN=$(terraform -chdir=cdktf.out/stacks/urlshortener-stack output -raw swa) \
npx --yes @azure/static-web-apps-cli deploy ./prod_static --env=production
rm -rf prod_static
