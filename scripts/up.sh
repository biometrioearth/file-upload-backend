#/usr/bin/env bash

environment="dev"
if [ "$1" != '' ]; then
  environment=$1
fi

docker-compose -f docker-compose.yml up -d \
  --remove-orphans \
  --force-recreate \
  --renew-anon-volumes