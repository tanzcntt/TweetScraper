#!/bin/bash
# shellcheck disable=SC2161
while true; do
  echo " Start set keyword "
  python3 bot-set-keywords.py -u https://gql.dhunt.io/ -t defaulttoken -m tweet
  sleep 6
done