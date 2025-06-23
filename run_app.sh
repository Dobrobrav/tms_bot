#!/bin/sh

docker rm -f bot_container 2>/dev/null || true
docker build --tag bot . && docker run --name bot_container bot
