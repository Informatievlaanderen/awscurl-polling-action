#!/bin/sh

# Check if the deploy_taget ($9) is set or not
if [ -z "$9" ]; then
  deploy_target="none"
else
  deploy_target="$9"
fi

python3 ./main.py \
--environment "$1" \
--version "$2" \
--status_url "$3" \
--deploy_url "$4" \
--access_key "$5" \
--secret_key "$6" \
--region "$7" \
--interval "$8" \
--deploy_target "$deploy_target";
