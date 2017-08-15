import os
import sys
import subprocess

import logging

import utils
from modules import jenkins, vicmachine
from modules.govc import build_env, upload

if __name__ == "__main__":
    try:
        import settings_local as settings
        print("Imported local settings.")
    except ImportError:
        import settings
        print("Imported default settings.")

    if "VERBOSE" in os.environ and os.environ["VERBOSE"].lower() == "true":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    args = sys.argv[1:]

    env = build_env(settings)

    if "CONTAINER_NAME" in os.environ:
        container_name = os.environ["CONTAINER_NAME"]

        docker_url, cert_path = vicmachine.load_config(settings)

        docker = utils.setup_docker_client(
            docker_url,
            cert_path
        )

        containers = docker.containers.list(
            filters={"name": jenkins.master.MASTER_IMAGE}
        )

        container = containers[0]

        env["GOVC_GUEST_LOGIN"] = container.id
        env["GOVC_VM"] = container.name + "-" + container.id[:12]

    if args[0] == "upload":
        upload(settings.gopath, env, args[1], args[2:])
    else:
        run(settings.gopath, env, args)
