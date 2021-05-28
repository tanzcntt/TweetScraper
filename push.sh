#!/bin/bash
# shellcheck disable=SC2161
while true; do
  echo " start push to  "
  python3 check-data-tw.py -u https://gql-dhunt.howtozweb.com -t defaulttoken -d 0
  echo " end push to  "
  sleep 6s
done