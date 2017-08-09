import subprocess
from typing import Optional, Tuple

import os

# ${VIC_BIN_PATH}/vic-machine-darwin create \
#     -t ${SERVER_PATH} \
#     -u="$SERVER_LOGIN_USERNAME" \
#     -p="$SERVER_LOGIN_PASSWORD" \
#     --image-store="vsanDatastore/vch/vch-imagestore" \
#     --volume-store="vsanDatastore/vch/vch-volumestore:volumestore" \
#     --volume-store="vsanDatastore/vch/vch-volumestore:default" \
#     --volume-store="nfs://${NFS_VOLUME}:nfs-store" \
#     --tls-cname="*.eng.vmware.com" \
#     --timeout 6m \
#     --name ${VCH_NAME} \
#     --bridge-network="bridge" \
#     --public-network=vm-network \
#     --container-network=external \
#     --insecure-registry=${REGISTRY_PATH} \
#     --registry-ca registry/ca.cert \
#     --thumbprint=${SERVER_THUMBPRINT} \
#     --base-image-size 100GB \
#     --debug 0

VOLUME_DRIVER="vsphere"

def process_args(param_name, *args):
    """Automatically argumentify any args and handle empty values."""

    out_args = []

    for arg in args:
        if len(arg) > 0:
            out_args.append("--{0}={1}".format(param_name, arg))

    return out_args


def delete(settings, **kwargs) -> bool:
    args = [
        settings.vic_machine_path,
        "delete",
        *process_args("t", settings.esx_url),
        *process_args("u", settings.esx_username),
        *process_args("p", settings.esx_password),
        *process_args("thumbprint", settings.esx_thumbprint),
        *process_args("compute-resource", settings.cluster_name),
        *process_args("name", settings.vch_name),
        *process_args("timeout", "10m"),
    ]

    result = subprocess.run(args)

    if result.returncode == 0:
        return True
    else:
        print("\n-------------------------------------------------------------")
        print("ERROR DELETING VCH")
        print("-------------------------------------------------------------")
        print("STDOOUT")
        print("-------------------------------------------------------------\n")
        print(result.stdout)
        print("\n-------------------------------------------------------------")
        print("STDERR")
        print("-------------------------------------------------------------\n")
        print(result.stderr)
        print("")
        return False


def deploy(settings, **kwargs) -> bool:
    args = [
        settings.vic_machine_path,
        "create",
        *process_args("t", settings.esx_url),
        *process_args("u", settings.esx_username),
        *process_args("p", settings.esx_password),
        *process_args("thumbprint", settings.esx_thumbprint),
        *process_args("tls-cname", settings.esx_tls_cname),
        *process_args("compute-resource", settings.cluster_name),
        *process_args("name", settings.vch_name),
        *process_args("image-store", *settings.image_stores),
        *process_args("volume-store", *settings.volume_stores),
        *process_args("registry-ca", *settings.registry_cas),
        *process_args("bridge-network", settings.bridge_network),
        *process_args("public-network", settings.public_network),
        *process_args("container-network", settings.container_network),
        *process_args("management-network", settings.management_network),
        *process_args("insecure-registry", *settings.insecure_repositories),
        *process_args("base-image-size", "50GB"),
        *process_args("debug", settings.debug),
        *process_args("timeout", "10m"),
    ]

    result = subprocess.run(args)

    if result.returncode == 0:
        return True
    else:
        print("\n-------------------------------------------------------------")
        print("ERROR DEPLOYING VCH")
        print("-------------------------------------------------------------")
        print("STDOOUT")
        print("-------------------------------------------------------------\n")
        print(result.stdout)
        print("\n-------------------------------------------------------------")
        print("STDERR")
        print("-------------------------------------------------------------\n")
        print(result.stderr)
        print("")
        return False


def load_config(settings) -> Tuple[Optional[str], Optional[str]]:
    name = settings.vch_name
    vch_path = os.path.join(os.path.curdir, name, name + ".env")

    if not os.path.exists(vch_path):
        return None, None

    with open(vch_path, "r") as f:
        lines = f.readlines()
        lines = lines[0].split(" ")

        env = {}

        for line in lines:
            line = line.split("=", 1)
            env[line[0]] = line[1]

    docker_url = env["DOCKER_HOST"]
    certificate_path = env["DOCKER_CERT_PATH"]

    return docker_url, certificate_path

MODULE = {
    "deploy": deploy,
    "delete": delete
}