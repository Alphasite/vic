import os
import ssl
import time

from docker import DockerClient
from docker.tls import TLSConfig
from jenkinsapi.jenkins import Jenkins

from modules.jenkins import master

CREDS_DESCRIPTION = 'ssh-key'


def get_ip(container, docker, settings):
    container_properties = docker.api.inspect_container(
        container.name
    )
    networks = container_properties["NetworkSettings"]["Networks"]
    network = networks[settings.container_network]
    return network["IPAddress"]


def get_jenkins_url(settings, docker):
    containers = docker.containers.list(filters={"name": master.MASTER_IMAGE})

    if len(containers) == 0:
        print("No master container running, cant configure it correctly.")
        return None

    master_container = containers[0]

    return "http://{ip}:8080".format(
        ip=get_ip(master_container, docker, settings)
    )


def connect_to_jenkins(settings, docker):
    return Jenkins(
        baseurl=get_jenkins_url(settings, docker),
        ssl_verify=False,
    )


def setup_docker_client(docker_url, cert_path):
    cert_path = os.fspath(cert_path)
    tls_config = TLSConfig(
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        client_cert=(
            os.path.join(cert_path, "cert.pem"),
            os.path.join(cert_path, "key.pem")
        ),
        ca_cert=os.path.join(cert_path, "ca.pem"),
    )

    docker = DockerClient(
        tls=tls_config,
        base_url=docker_url,
        timeout=240,
    )

    docker.ping()

    return docker


def populate_env(env, container):
    env["GOVC_GUEST_LOGIN"] = container.id
    env["GOVC_VM"] = container.name

    return env


def find_and_kill_running_instances(docker, name):
    print("Checking if container already exists")

    containers = docker.containers.list(
        all=True,
        filters={"name": name}
    )

    if len(containers) > 0:
        print("Container already exists, killing and restarting.")

        container = containers[0]

        if container.status == "running":
            container.kill()
            container.reload()

        while container.status == "running":
            print("Container still running...")
            time.sleep(5)
            container.reload()

        container.remove()
    else:
        print("Container doesnt exist...")
