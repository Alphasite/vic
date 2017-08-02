#!/usr/bin/env bash

URL_ARRAY="${ESX_HOST_0} ${ESX_HOST_1} ${ESX_HOST_2} ${ESX_HOST_3}"

docker ${DOCKER_FLAGS} run                                                      \
    -e BIN=bin                                                                  \
    -e GOPATH=/go                                                               \
    -e SHELL=/bin/bash                                                          \
    -e LOG_TEMP_DIR=install-logs                                                \
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
    -v $GOPATH:/go                                                              \
    -w /go/src/github.com/vmware/vic                                            \
    --privileged                                                                \
    gcr.io/eminent-nation-87317/vic-integration-test:1.34                       \
    $@

exit $?
