#!/usr/bin/env bash
export LANG=en_US.UTF-8

if [ "$IS_HOST_NETWORK" == "1" ]; then
    PORT=$PORT0
else
    PORT=9416
fi
echo service port is: $PORT

export SERVICE_NAME_ENV="vision_service"
exec python3 server.py --port=$PORT --worker=2
