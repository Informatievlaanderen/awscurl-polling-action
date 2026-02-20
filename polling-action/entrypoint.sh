#!/bin/sh

if [ -z "$7" ]; then
  interval=2
else
  interval="$7"
fi

if [ -z "$8" ]; then
  region="eu-west-1"
else
  region="$8"
fi

# Check if the deploy_taget ($9) is set or not
if [ -z "$9" ]; then
  deploy_target="none"
else
  deploy_target="$9"
fi

if [ -z "${10}" ]; then
  domain="none"
else
  domain="${10}"
fi

if [ -z "${11}" ]; then
  project="none"
else
  project="${11}"
fi

if [ -z "${12}" ]; then
  application="none"
else
  application="${12}"
fi

python3 /main.py \
--environment "$1" \
--version "$2" \
--status_url "$3" \
--deploy_url "$4" \
--access_key "$5" \
--secret_key "$6" \
-i "$interval" \
-r "$region" \
--deploy_target "$deploy_target" \
--domain "$domain" \
--project "$project" \
--application "$application" \
--use_subfolder "${13}"