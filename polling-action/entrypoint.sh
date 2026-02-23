#!/bin/sh

if [ -z "$6" ]; then
  interval=2
else
  interval="$6"
fi

if [ -z "$7" ]; then
  region="eu-west-1"
else
  region="$7"
fi

# Check if the deploy_taget (${8}) is set or not
if [ -z "${8}" ]; then
  deploy_target="none"
else
  deploy_target="${8}"
fi

if [ -z "${9}" ]; then
  domain="none"
else
  domain="${9}"
fi

if [ -z "${10}" ]; then
  project="none"
else
  project="${10}"
fi

if [ -z "${11}" ]; then
  application="none"
else
  application="${11}"
fi

python3 /main.py \
--environment "$1" \
--version "$2" \
--status_url "$3" \
--deploy_url "$4" \
--role_arn "$5" \
-i "$interval" \
-r "$region" \
--deploy_target "$deploy_target" \
--domain "$domain" \
--project "$project" \
--application "$application" \
--use_subfolder "${12}"