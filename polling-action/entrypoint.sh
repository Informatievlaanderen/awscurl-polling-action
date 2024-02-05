#!/bin/sh

# Check if the deploy_taget ($9) is set or not
if [ -z "$8" ]; then
  deploy_target="none"
else
  deploy_target="$8"
fi

if [ -z "$9" ]; then
  domain="none"
else
  domain="$9"
fi

if [ -z "$10" ]; then
  project="none"
else
  project="$10"
fi

python3 /main.py \
--environment "$1" \
--version "$2" \
--status_url "$3" \
--deploy_url "$4" \
--access_key "$5" \
--secret_key "$6" \
--interval "$7" \
--deploy_target "$deploy_target" \
--domain "$domain" \
--project "$project";
