#!/usr/bin/env bash

echo HELLO WORLD!

source /vch-creds/*.env

/docker/docker -v
/docker/docker -H ${DOCKER_HOST} --tlsverify --tlscacert="/vch-creds/ca.pem" --tlscert="/vch-creds/cert.pem" --tlskey="/vch-creds/key.pem" info
/docker/docker -H ${DOCKER_HOST} --tlsverify --tlscacert="/vch-creds/ca.pem" --tlscert="/vch-creds/cert.pem" --tlskey="/vch-creds/key.pem" run hello-world
