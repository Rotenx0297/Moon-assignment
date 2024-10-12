How to run script:
* python3 check_sqs_policy.py -aid <account_id> -rta <role_to_assume> -dbt <destination_bucket> -md <running_mode>

Flow:
* Created in docker hub a docker base image called "rotem-base" containing aws credentials and role with permissions to access my private AWS Account (ID: 503161568134)
* Adjusted the Dockerfile to run from the base image and pack the script to a new image in docker hub called "moon-assignment"
* Github workflow configuration is in the path .github/workflows/python-docker-publish.yml
* The successfull #22 build was run on my private AWS Account and produced the log file in source: s3://rotenx/sqs_names_log.txt
