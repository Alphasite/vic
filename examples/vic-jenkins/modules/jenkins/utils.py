from jenkinsapi.jenkins import Jenkins

from modules.jenkins import master
from utils import get_ip

CREDS_DESCRIPTION = 'ssh-key'


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
