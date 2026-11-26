#!/usr/bin/env fish
# À sourcer : source scripts/use-lab-env.fish
set -gx TP4_ROOT (path resolve (path dirname (status filename))/..)
umask 077
mkdir -p "$TP4_ROOT/.secrets/login-cache" "$TP4_ROOT/downloads"
chmod 700 "$TP4_ROOT/.secrets" "$TP4_ROOT/.secrets/login-cache"
touch "$TP4_ROOT/.secrets/config" "$TP4_ROOT/.secrets/credentials"
chmod 600 "$TP4_ROOT/.secrets/config" "$TP4_ROOT/.secrets/credentials"
set -gx AWS_CONFIG_FILE "$TP4_ROOT/.secrets/config"
set -gx AWS_SHARED_CREDENTIALS_FILE "$TP4_ROOT/.secrets/credentials"
set -gx AWS_LOGIN_CACHE_DIRECTORY "$TP4_ROOT/.secrets/login-cache"
# AWS_PAGER attend une commande : la chaîne vide le désactive.
set -gx AWS_PAGER ""
set -gx AWS_CLI_AUTO_PROMPT off
set -gx AWS_EC2_METADATA_DISABLED true
set -gx AWS_IGNORE_CONFIGURED_ENDPOINT_URLS true
set -gx AWS_PROFILE tp2a-admin
for name in AWS_DEFAULT_PROFILE AWS_DEFAULT_REGION AWS_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN AWS_WEB_IDENTITY_TOKEN_FILE AWS_ROLE_ARN AWS_ROLE_SESSION_NAME AWS_CONTAINER_CREDENTIALS_FULL_URI AWS_CONTAINER_CREDENTIALS_RELATIVE_URI AWS_CONTAINER_AUTHORIZATION_TOKEN AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE AWS_ENDPOINT_URL AWS_ENDPOINT_URL_STS AWS_ENDPOINT_URL_DYNAMODB AWS_ENDPOINT_URL_IAM
    set -e $name
end
