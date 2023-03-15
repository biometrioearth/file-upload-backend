#/usr/bin/env bash

# $2:-v (volumes)

environment="dev"
if [ "$1" != '' ]; then
  environment=$1
fi

docker-compose -f docker-compose.yml down $2