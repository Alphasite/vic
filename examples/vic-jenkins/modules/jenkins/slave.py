import json
import os
import shutil
import traceback
import urllib
from xml.etree import ElementTree

import requests
import urllib3
from docker import DockerClient

import govc
from modules import vicmachine
from modules.jenkins import utils

SLAVE_VOLUME = "jenkins-slave"
SLAVE_IMAGE = "jenkins-slave"
SLAVE_DOCKER_CACHE_VOLUME = "jenkins-slave-docker"


def build_slave(settings, **kwargs) -> bool:
    print("Setting up connection to local docker client")
    docker = DockerClient()

    print("Generating configs for image")
    config_dir = "jenkins-slave/config"

    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    # SSH key for slave.

    pub_key = "jenkins-ssh-keys/jenkins_ssh.pub"
    authorized_keys = os.path.join(config_dir, "authorized_keys")
    shutil.copyfile(pub_key, authorized_keys)

    # # Registry CA
    #
    # shutil.copyfile(
    #     "registry/ca.cert",
    #     os.path.join(
    #         config_dir,
    #         "docker",
    #         "certs.d",
    #         "{registry}".format(registry=settings.repository_url),
    #         "ca.cert"
    #     )
    # )

    # Upload insecure registry config to server.

    daemon_config_file = os.path.join(config_dir, "daemon.json")

    daemon_config = {
        "insecure-registries": settings.insecure_repositories
    }

    with open(daemon_config_file, "w") as f:
        json.dump(daemon_config, f)

    print("Building image...")

    image = docker.images.build(
        tag="jenkins-slave",
        path="jenkins-slave",
        rm=True,
    )

    versioned_tag = SLAVE_IMAGE + ":latest"

    remote_tag = "{0}/{1}/{2}:latest".format(
        settings.repository_url,
        settings.repository_group,
        SLAVE_IMAGE,
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

    return True


def deploy_slave(settings, docker_url, cert_path) -> bool:
    print("Connecting to docker client")

    docker = utils.setup_docker_client(docker_url, cert_path)

    print("Creating/Discovering volumes")
    volumes = docker.volumes.list(filters={"name": SLAVE_VOLUME})

    if len(volumes) == 0:
        docker.volumes.create(
            SLAVE_VOLUME,
            driver=vicmachine.VOLUME_DRIVER,
            driver_opts={
                # "VolumeStore": "nfs-store",
                "Capacity": "10GB",
            },
        )

    volumes = docker.volumes.list(filters={"name": SLAVE_DOCKER_CACHE_VOLUME})

    if len(volumes) == 0:
        docker.volumes.create(
            SLAVE_DOCKER_CACHE_VOLUME,
            driver=vicmachine.VOLUME_DRIVER,
            driver_opts={
                # "VolumeStore": "nfs-store",
                "Capacity": "11GB",
            },
        )

    print("Pulling latest base image")

    remote_tag = "{0}/{1}/{2}:latest".format(
        settings.repository_url,
        settings.repository_group,
        SLAVE_IMAGE,
    )

    docker.images.pull(remote_tag)

    utils.find_and_kill_running_instances(docker, SLAVE_IMAGE)

    print("Starting container")

    container = docker.containers.run(
        remote_tag,
        name=SLAVE_IMAGE,
        network=settings.container_network,
        mem_limit="8g",
        cpuset_cpus="4",
        environment={
            'VCH_URL': docker_url,
            'VCH_CERT_PATH': "/var/jenkins_home/docker_certs",
        },
        ports={
            '22/tcp': None,
            '22/udp': None,
            '2376/tcp': None,
            '2376/udp': None,
        },
        volume_driver=vicmachine.VOLUME_DRIVER,
        volumes={
            SLAVE_VOLUME: {"bind": "/var/jenkins_home", "mode": "rw"},
            SLAVE_DOCKER_CACHE_VOLUME: {"bind": "/var/lib/docker", "mode": "rw"},
        },
        detach=True,
    )

    print("Storing vch credentials")
    env = govc.build_env(settings)
    env = utils.populate_env(env, container)
    env["GOVC_GUEST_LOGIN"] = container.id
    env["GOVC_VM"] = container.name + "-" + container.id[:12]

    files = os.listdir(cert_path)
    files = [os.path.join(cert_path, file) for file in files]

    destination = "/var/jenkins_home/docker_certs"
    govc.run(settings.gopath, env, ["guest.mkdir", destination])
    govc.upload(settings.gopath, env, destination, files)

    ip = utils.get_ip(container, docker, settings)

    print("Slave started with ip", ip)

    try:
        register_slave_with_master(docker_url, docker, ip, settings)
    except:
        print("Error configuring slave")
        print()
        traceback.print_exc()
        print()
        print("Cleaning up slave")
        print()

        utils.find_and_kill_running_instances(docker, SLAVE_IMAGE)

    return True


def register_slave_with_master(docker_url, docker, ip, settings):
    jenkins = utils.connect_to_jenkins(settings, docker)

    # print("Uploading certificates & config...")
    #
    # env = govc.build_env(settings)
    # env = populate_env(env, container)
    # env["GOVC_GUEST_LOGIN"] = container.id
    # env["GOVC_VM"] = container.name + "-" + container.id[:12]
    #
    # # Upload SSH key for slave.
    #
    # pub_key = "jenkins-ssh-keys/jenkins_ssh.pub"
    # authorized_keys = "jenkins-ssh-keys/authorized_keys"
    # shutil.copyfile(pub_key, authorized_keys)
    #
    # destination = "/root/.ssh/"
    #
    # govc.run(env, ["guest.mkdir", destination])
    # govc.upload(env, destination, [authorized_keys])
    # govc.run(env, ["guest.chmod", "0600", destination + "/authorized_keys"])
    #
    # # Upload registry CA
    #
    # registry_ca = "registry/ca.cert"
    #
    # destination = "/etc/docker/certs.d/{registry}".format(
    #     registry=settings.repository_url
    # )
    #
    # govc.run(env, ["guest.mkdir", destination])
    # govc.upload(env, destination, [registry_ca])
    #
    # # Upload insecure registry config to server.
    #
    # tempdir = tempfile.mkdtemp()
    # daemon_config_file = os.path.join(tempdir, "daemon.json")
    #
    # daemon_config = {
    #     "insecure-registries": settings.insecure_repositories
    # }
    #
    # with open(daemon_config_file, "w") as f:
    #     json.dump(daemon_config, f)
    #
    # destination = "/etc/docker/"
    #
    # govc.upload(env, destination, [daemon_config_file])

    print("Registering slave on master")

    node_dict = {
        'num_executors': 2,
        'node_description': 'ssh-node',
        'remote_fs': '/var/jenkins_home',
        'labels': 'slave',
        'exclusive': False,
        'host': ip,
        'port': 22,
        'credential_description': utils.CREDS_DESCRIPTION,
        'jvm_options': '-Xmx1000M',
        'java_path': '/bin/java',
        'prefix_start_slave_cmd': '',
        'suffix_start_slave_cmd': '',
        'max_num_retries': 0,
        'retry_wait_time': 0,
        'retention': 'Always',
        'ondemand_delay': 1,
        'ondemand_idle_delay': 5,
        'env': [
            {
                'key': 'VCH_CERT_PATH',
                'value': "/var/jenkins_home/docker_certs",
            },
            {
                'key': 'VCH_URL',
                'value': docker_url,
            }
        ]
    }


    node_name = "ssh-node"
    nodes = jenkins.nodes

    if node_name in nodes:
        del nodes[node_name]

    node = jenkins.nodes.create_node(node_name, node_dict)

    # Patch the node config to disable host key verification; the jenkins API
    # exposes no way to do it properly, so for now im doing this hack.
    config = node.get_config()
    config = ElementTree.fromstring(config)

    ElementTree.SubElement(
        config[6],
        "sshHostKeyVerificationStrategy",
        attrib={
            "class": "hudson.plugins.sshslaves.verifiers"
                     ".NonVerifyingKeyVerificationStrategy",
        }
    )

    config = ElementTree.tostring(config).decode("utf-8")

    node.upload_config(config)

    print("Created SSH Node")
    node.pprint()

    with open(os.path.join("jenkins-utils", "configure-yadocker-cloud.groovy")) as f:
        docker_cloud_config_script = f.read()

    remote_tag = "{0}/{1}/{2}:latest".format(
        settings.repository_url,
        settings.repository_group,
        SLAVE_IMAGE,
    )

    ssh_credentials = jenkins.credentials[utils.CREDS_DESCRIPTION]

    docker_cloud_config_script = docker_cloud_config_script.replace(
        "DOCKER_URL",
        "tcp://{ip}:2376".format(ip=ip)
    )

    docker_cloud_config_script = docker_cloud_config_script.replace(
        "DOCKER_IMAGE",
        remote_tag,
    )

    docker_cloud_config_script = docker_cloud_config_script.replace(
        "SSH_CREDENTIALS_ID",
        ssh_credentials.credential_id,
    )

    response = requests.post(
        "{url}/scriptText".format(url=utils.get_jenkins_url(settings, docker)),
        {"script": docker_cloud_config_script}
    )

    if response.ok:
        print("Configured Docker cloud")
        print(response.content)
    else:
        print("Failed to configure docker cloud correctly")

MODULE = {
    "build": build_slave,
    "deploy": deploy_slave,
}