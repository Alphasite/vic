#!/usr/bin/env bash

URL_ARRAY="${ESX_HOST_0} ${ESX_HOST_1} ${ESX_HOST_2} ${ESX_HOST_3}"

docker ${DOCKER_FLAGS} run                                                      \
    -e TEST_BUILD_IMAGE=""                                                      \
    -e TEST_URL_ARRAY= "${URL_ARRAY}"                                           \
    -e TEST_RESOURCE="/${DATACENTER_NAME}/host/${CLUSTER_NAME}"                 \
    -e TEST_TIMEOUT=60s                                                         \
    -e VIC_ESX_TEST_DATASTORE="/${DATACENTER_NAME}/datastore/${DATASTORE_NAME}" \
    -e VIC_ESX_TEST_URL="${ESX_USERNAME}:${ESX_PASSWORD}@${ESX_URL}"            \
    -e BIN=bin                                                                  \
    -e GOPATH=/go                                                               \
    -e SHELL=/bin/bash                                                          \
    -e TEST_USERNAME=${ESX_USERNAME}                                            \
    -e TEST_PASSWORD=${ESX_PASSWORD}                                            \
    -e TEST_DATASTORE=${DATASTORE_NAME}                                         \
    -e TEST_RESOURCE=${CLUSTER_NAME}                                            \
    -e TEST_TIMEOUT=60s                                                         \
    -e GOVC_USERNAME=${ESX_USERNAME}                                            \
    -e GOVC_PASSWORD=${ESX_PASSWORD}                                            \
    -e GOVC_DATACENTER=${DATACENTER_NAME}                                       \
    -e GOVC_DATASTORE=${DATASTORE_NAME}                                         \
    -e GOVC_RESOURCE_POOL=${CLUSTER_NAME}                                       \
    -e GOVC_HOST=${ESX_URL}                                                     \
    -e GOVC_INSECURE=true                                                       \
    -e BRIDGE_NETWORK=${BRIDGE_NETWORK}                                         \
    -e PUBLIC_NETWORK=${PUBLIC_NETWORK}                                         \
    -e DOMAIN=${ESX_TLS_CNAME}                                                  \
    -e DRONE_BUILD_NUMBER=${DRONE_BUILD_NUMBER}                                 \
    -v ${GOPATH}:/go                                                            \
    -w /go/src/github.com/vmware/vic                                            \
    --privileged                                                                \
    gcr.io/eminent-nation-87317/vic-integration-test:1.33                       \
    $@
