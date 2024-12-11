#!/bin/sh

TAG=${1:-latest}
docker pull filipmania/urlshortener:$TAG

docker create --name url-temp filipmania/urlshortener:$TAG
docker cp url-temp:/opt/prod_static ./prod_static
docker rm url-temp

touch prod_static/index.html
SWA_CLI_DEPLOYMENT_TOKEN=$(terraform -chdir=cdktf.out/stacks/urlshortener-stack output -raw swa) \
npx --yes @azure/static-web-apps-cli deploy ./prod_static --env=production
rm -rf prod_static
