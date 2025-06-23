#!/bin/sh

docker build --pull --tag bot . && docker run --name bot_container bot
