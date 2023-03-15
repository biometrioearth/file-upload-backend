#!/usr/bin/env bash

# 1=<service_name>
docker-compose -f docker-compose.yml kill $1
wait
docker-compose -f docker-compose.yml rm $1
wait
docker-compose -f docker-compose.yml up -d --renew-anon-volumes $1