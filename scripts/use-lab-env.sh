#!/usr/bin/env bash
# À sourcer : source scripts/use-lab-env.sh
TP4_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
export TP4_ROOT
umask 077
mkdir -p "$TP4_ROOT/.secrets/login-cache" "$TP4_ROOT/downloads"
chmod 700 "$TP4_ROOT/.secrets" "$TP4_ROOT/.secrets/login-cache"
touch "$TP4_ROOT/.secrets/config" "$TP4_ROOT/.secrets/credentials"
chmod 600 "$TP4_ROOT/.secrets/config" "$TP4_ROOT/.secrets/credentials"
export AWS_CONFIG_FILE="$TP4_ROOT/.secrets/config"
export AWS_SHARED_CREDENTIALS_FILE="$TP4_ROOT/.secrets/credentials"
export AWS_LOGIN_CACHE_DIRECTORY="$TP4_ROOT/.secrets/login-cache"
# AWS_PAGER est une commande, pas un chemin de stockage. Vide = aucun pager.
export AWS_PAGER=""
export AWS_CLI_AUTO_PROMPT=off
export AWS_EC2_METADATA_DISABLED=true
export AWS_IGNORE_CONFIGURED_ENDPOINT_URLS=true
export AWS_PROFILE=tp2a-admin
unset AWS_DEFAULT_PROFILE AWS_DEFAULT_REGION AWS_REGION
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN
unset AWS_WEB_IDENTITY_TOKEN_FILE AWS_ROLE_ARN AWS_ROLE_SESSION_NAME
unset AWS_CONTAINER_CREDENTIALS_FULL_URI AWS_CONTAINER_CREDENTIALS_RELATIVE_URI
unset AWS_CONTAINER_AUTHORIZATION_TOKEN AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE
unset AWS_ENDPOINT_URL AWS_ENDPOINT_URL_STS AWS_ENDPOINT_URL_DYNAMODB AWS_ENDPOINT_URL_IAM
