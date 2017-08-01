import os
import sys
import subprocess

import logging

from modules import jenkins, vicmachine


def build_env(settings):
    env = {}
    env.update(os.environ)
    env["GOVC_URL"] = settings.esx_url
    env["GOVC_USERNAME"] = settings.esx_username
    env["GOVC_PASSWORD"] = settings.esx_password
    env["GOVC_INSECURE"] = "1"

    for key, value in os.environ.items():
        if "GOVC" in key:
            print(key, value)

    return env


def run(gopath, env, args):
    args = [gopath + "/bin/govc"] + args

    command = subprocess.Popen(args, env=env)
    command.communicate()


def upload(gopath, env, destination, files):
    for file in files:
        file_name = os.path.split(file)[-1:][0]

        command = [
            "guest.upload",
            file,
            os.path.join(destination, file_name)
        ]

        run(gopath, env, command)

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

        docker = jenkins.utils.setup_docker_client(
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
