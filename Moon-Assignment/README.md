How to run script:
* Run from EC2 - Attach IAM role with relevant permissions
OR
* Run from Local Machine - Make sure to use credentials and role role arn to assume with source profile:
[profile]
aws_access_key_id=
aws_secret_access_key=
aws_session_token=

[rotem-profile]
role_arn = <role_to_assume>
source_profile = <profile>

* python3 check_sqs_policy.py -aid <account_id> -rta <role_to_assume> -dbt <destination_bucket> -md <running_mode>
