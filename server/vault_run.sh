#!/bin/sh
docker rm vault
docker run -ti --name vault -p 5000:8080 -v "/root/:/conf/" vault
