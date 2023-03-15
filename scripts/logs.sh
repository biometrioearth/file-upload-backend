#!/usr/bin/env bash

# -f : hang to logs screen
# 1=<service_name>
docker-compose -f docker-compose.yml logs -f $1