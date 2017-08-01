import os

from docker import DockerClient
from jenkinsapi.credential import SSHKeyCredential
from jenkinsapi.jenkins import Jenkins

import govc
from modules import vicmachine
from modules.jenkins import slave, utils

MASTER_VOLUME = "jenkins-master"
MASTER_IMAGE = "jenkins-master"


def build_master(settings):
    print("Setting up connection to local docker client")

    docker = DockerClient()

    print("Building image...")

    image = docker.images.build(
        tag="jenkins-master",
        path="jenkins-master",
        rm=True,
    )

    versioned_tag = slave.SLAVE_IMAGE + ":latest"

    remote_tag = "{0}/{1}/{2}:latest".format(
        settings.repository_url,
        settings.repository_group,
        MASTER_IMAGE,
    )

    print("Tagging image")

    image.tag(versioned_tag)
    image.tag(remote_tag)

    print("Pushing image {0}...".format(remote_tag))

    docker.images.push(
        repository=remote_tag,
        auth_config={
            "username": settings.repository_user,
            "password": settings.repository_password,
        }
    )

    print("Successfully pushed image to repository")


def deploy_master(settings, docker_url, cert_path) -> bool:
    remote_tag = "{0}/{1}/{2}:latest".format(
        settings.repository_url,
        settings.repository_group,
        MASTER_IMAGE,
    )

    print("Connecting to docker client")
    docker = utils.setup_docker_client(docker_url, cert_path)

    print("Creating/Discovering volumes")
    volumes = docker.volumes.list(filters={"name": MASTER_VOLUME})

    if len(volumes) == 0:
        volume = docker.volumes.create(
            MASTER_VOLUME,
            driver=vicmachine.VOLUME_DRIVER
        )
    else:
        volume = volumes[0]

    print("Pulling latest base image")

    docker.images.pull(remote_tag)

    utils.find_and_kill_running_instances(docker, MASTER_IMAGE)

    print("Starting container")

    container = docker.containers.run(
        remote_tag,
        name=MASTER_IMAGE,
        command=[
            "--argumentsRealm.passwd.{username}={password}".format(
                username=settings.jenkins_admin_username,
                password=settings.jenkins_admin_password,
            ),
            "--argumentsRealm.roles.{username}=admin".format(
                username=settings.jenkins_admin_username,
            ),
        ],
        environment={
            "JAVA_OPTS": "-Djenkins.install.runSetupWizard=false",
        },
        network=settings.container_network,
        ports={
            '8080/tcp': None,
            '8080/udp': None,
            '50000/tcp': None,
            '50000/udp': None,
        },
        volume_driver=vicmachine.VOLUME_DRIVER,
        volumes={
            MASTER_VOLUME: {"bind": "/var/jenkins_home", "mode": "rw"}
        },
        detach=True
    )

    ip = utils.get_ip(container, docker, settings)

    print("Deployed jenkins to ip:", ip + ":8080")
    print(
        "Admin credentials are Username: {username} Password: {password}".format(
            username=settings.jenkins_admin_username,
            password=settings.jenkins_admin_password,
        )
    )

    return True


def configure_master(settings, docker_url, cert_path):
    print("Setting up docker")
    docker = utils.setup_docker_client(docker_url, cert_path)
    containers = docker.containers.list(filters={"name": MASTER_IMAGE})

    if len(containers) > 0:
        container = containers[0]

        print("Finding IP of container...")
        ip = utils.get_ip(container, docker, settings)

        while len(ip) == 0:
            ip = utils.get_ip(container, docker, settings)
            container.reload()

        jenkins_url = "http://{ip}:8080".format(ip=ip)

        jenkins = Jenkins(jenkins_url)
        creds = jenkins.credentials

        print("Storing container credentials")
        env = govc.build_env(settings)
        env = utils.populate_env(env, container)
        env["GOVC_GUEST_LOGIN"] = container.id
        env["GOVC_VM"] = container.name + "-" + container.id[:12]

        files = os.listdir(cert_path)
        files = [os.path.join(cert_path, file) for file in files]

        destination = "/var/jenkins_home/docker_certs"
        govc.run(settings.gopath, env, ["guest.mkdir", destination])
        govc.upload(settings.gopath, env, destination, files)

        with open("jenkins-ssh-keys/jenkins_ssh") as f:
            private_key = f.read()

        cred_dict = {
            'description': utils.CREDS_DESCRIPTION,
            'userName': 'root',
            'passphrase': '',
            'private_key': private_key
        }

        if utils.CREDS_DESCRIPTION in creds:
            del creds[utils.CREDS_DESCRIPTION]

        creds[utils.CREDS_DESCRIPTION] = SSHKeyCredential(cred_dict)

    else:
        print("Failed tp find the container to configure.")
        return
