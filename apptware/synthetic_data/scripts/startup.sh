#!/bin/bash
supervisord -n
# bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:9000)" != "200" ]]; do sleep 5; done'