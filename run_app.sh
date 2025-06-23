#!/bin/sh

docker build --tag bot . && docker run --name bot_container bot
