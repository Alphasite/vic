import os
import subprocess

import utils


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


def run_wrapper(settings, arguments, **kwargs) -> bool:
    env = build_env(settings)
    run(settings.gopath, env, arguments)
    return True


def upload(gopath, env, destination, files):
    for file in files:
        file_name = os.path.split(file)[-1:][0]

        command = [
            "guest.upload",
            file,
            os.path.join(destination, file_name)
        ]

        run(gopath, env, command)


def upload_wrapper(settings, arguments, docker_url, cert_path, **kwargs) -> bool:
    env = build_env(settings)

    if "CONTAINER_NAME" in os.environ:
        container_name = os.environ["CONTAINER_NAME"]

        docker = utils.setup_docker_client(
            docker_url,
            cert_path
        )

        containers = docker.containers.list(
            filters={"name": container_name}
        )

        container = containers[0]

        env["GOVC_GUEST_LOGIN"] = container.id
        env["GOVC_VM"] = container.name + "-" + container.id[:12]

    upload(settings.gopath, env, arguments[0], arguments[:1])
    return True


MODULE = {
    "": run_wrapper,
    "upload": upload_wrapper,
}
