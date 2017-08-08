#!/usr/bin/env bash

IMAGE=${IMAGE:-gcr.io/eminent-nation-87317/vic-integration-test:1.33}

TEST_URL_ARRAY="${ESX_HOST_0} ${ESX_HOST_1} ${ESX_HOST_2} ${ESX_HOST_3}"

docker ${DOCKER_FLAGS} run                                                      \
    -e BIN=bin                                                                  \
    -e GOPATH=/go                                                               \
    -e SHELL=/bin/bash                                                          \
    -e LOG_TEMP_DIR=install-logs                                                \
    -e GITHUB_AUTOMATION_API_KEY="${GITHUB_AUTOMATION_API_KEY}"                 \
    -e DRONE_BUILD_NUMBER=${DRONE_BUILD_NUMBER}                                 \
    -e TEST_URL_ARRAY="${TEST_URL_ARRAY}"                                       \
    -e TEST_USERNAME="${TEST_USERNAME}"                                         \
    -e TEST_PASSWORD="${TEST_PASSWORD}"                                         \
    -e TEST_DATASTORE="${TEST_DATASTORE}"                                       \
    -e TEST_TIMEOUT="${TEST_TIMEOUT}"                                           \
    -e GOVC_INSECURE=true                                                       \
    -e GOVC_USERNAME="${TEST_USERNAME}"                                         \
    -e GOVC_PASSWORD="${TEST_PASSWORD}"                                         \
    -e GOVC_DATASTORE="${TEST_DATASTORE}"                                       \
    -e BRIDGE_NETWORK="${BRIDGE_NETWORK}"                                       \
    -e PUBLIC_NETWORK="${PUBLIC_NETWORK}"                                       \
    -e container_network="${container_network}"                                 \
    -e MANAGEMENT_NETWORK="${MANAGEMENT_NETWORK}"                               \
    -e DOMAIN="${DOMAIN}"                                                       \
    -e PY_BOT_ARGS="${PY_BOT_ARGS}"                                             \
    -v $GOPATH:/go                                                              \
    -w /go/src/github.com/vmware/vic                                            \
    --privileged                                                                \
    ${IMAGE}                                                                    \
    $@

exit $?
