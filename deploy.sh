#!/bin/bash

set -e

scp -P "$SERVER_PORT" "$SERVER_USER@$SERVER_IP_ADDRESS":~/igorlazerev-ru/tmp/site.zip site.zip
