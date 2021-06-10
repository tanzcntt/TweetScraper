#!/bin/bash
# shellcheck disable=SC2161
while true; do
  echo " Start "
  scrapy crawl TweetScraper -a query="\$ada OR #cardano OR #ada" -a mode=latest
  sleep 6
done