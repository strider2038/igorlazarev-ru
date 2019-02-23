#!/bin/bash

set -e

scp -P "$SERVER_PORT" -i ./deploy_key site.zip "$SERVER_USER@$SERVER_IP_ADDRESS":~/igorlazarev.ru/tmp/site.zip

ssh -p "$SERVER_PORT" -i ./deploy_key -q "$SERVER_USER@$SERVER_IP_ADDRESS" <<EOF
unzip ~/igorlazarev.ru/tmp/site.zip -d ~/igorlazarev.ru/tmp
rm -rf ~/igorlazarev.ru/public
mv ~/igorlazarev.ru/tmp/_site ~/igorlazarev.ru/public
rm -rf ~/igorlazarev.ru/tmp/*
EOF
