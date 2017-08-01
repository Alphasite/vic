from os import environ

vic_machine_path = environ["VIC_MACHINE_PATH"]

esx_url = environ["ESX_URL"]
esx_username = environ["ESX_USERNAME"]
esx_password = environ["ESX_PASSWORD"]
esx_thumbprint = environ["ESX_THUMBPRINT"]
esx_tls_cname = environ["ESX_TLS_CNAME"]

esx_hosts = []

i = 0
while "ESX_HOST_" + str(i) in environ:
    esx_hosts.append(environ["ESX_HOST_" + str(i)])
    i += 1

cluster_name = environ["CLUSTER_NAME"]

vch_name = environ["VCH_NAME"]

image_stores = [
    environ["IMAGE_STORE"]
]

volume_stores = [
    environ["VOLUME_STORE"],
    environ["NFS_VOLUME_STORE"],
]

registry_cas = [
    environ["REGISTRY_CA"]
]

bridge_network = environ["BRIDGE_NETWORK"]
public_network = environ["PUBLIC_NETWORK"]
container_network = environ["CONTAINER_NETWORK"]
management_network = environ["MANAGEMENT_NETWORK"]

repository_url = environ["REGISTRY_URL"]
repository_user = environ["REGISTRY_USER"]
repository_password = environ["REGISTRY_PASSWORD"]
repository_group = environ["REGISTRY_GROUP"]

insecure_repositories = [
    environ["INSECURE_REGISTRY"],
]

jenkins_admin_username = environ["JENKINS_ADMIN_USERNAME"]
jenkins_admin_password = environ["JENKINS_ADMIN_PASSWORD"]

datastore_name = environ["DATASTORE_NAME"]

gopath = environ["GOPATH"]

debug = environ["DEBUG"]
