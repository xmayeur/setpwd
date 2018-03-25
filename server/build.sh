#!/bin/sh

git pull

docker rm -f vault

docker build -t vault . && \
docker tag vault xmayeur/vault && \
#docker push xmayeur/vault

chmod +x vault_run.sh build.sh
sudo cp vault_run.sh /root

exec ./vault_run.sh



