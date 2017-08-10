from os import environ

def get_or_default(environ, key, default=""):
    if key in environ:
        return environ[key]
    else:
        return default

vic_machine_path = get_or_default(environ, "VIC_MACHINE_PATH")

esx_url = get_or_default(environ, "ESX_URL")
esx_username = get_or_default(environ, "ESX_USERNAME")
esx_password = get_or_default(environ, "ESX_PASSWORD")
esx_thumbprint = get_or_default(environ, "ESX_THUMBPRINT")
esx_tls_cname = get_or_default(environ, "ESX_TLS_CNAME")

esx_hosts = []

i = 0
while "ESX_HOST_" + str(i) in environ:
    esx_hosts.append(environ["ESX_HOST_"+ str(i)])
    i += 1

cluster_name = get_or_default(environ, "CLUSTER_NAME")

vch_name = get_or_default(environ, "VCH_NAME")

image_stores = [
    get_or_default(environ, "IMAGE_STORE")
]

volume_stores = [
    get_or_default(environ, "VOLUME_STORE"),
    get_or_default(environ, "NFS_VOLUME_STORE"),
]

registry_cas = [
    get_or_default(environ, "REGISTRY_CA")
]

bridge_network = get_or_default(environ, "BRIDGE_NETWORK")
public_network = get_or_default(environ, "PUBLIC_NETWORK")
container_network = get_or_default(environ, "CONTAINER_NETWORK")
management_network = get_or_default(environ, "MANAGEMENT_NETWORK")

repository_url = get_or_default(environ, "REGISTRY_URL")
repository_user = get_or_default(environ, "REGISTRY_USER")
repository_password = get_or_default(environ, "REGISTRY_PASSWORD")
repository_group = get_or_default(environ, "REGISTRY_GROUP")

insecure_repositories = [
    get_or_default(environ, "INSECURE_REGISTRY"),
]

jenkins_admin_username = get_or_default(environ, "JENKINS_ADMIN_USERNAME")
jenkins_admin_password = get_or_default(environ, "JENKINS_ADMIN_PASSWORD")

datastore_name = get_or_default(environ, "DATASTORE_NAME")

gopath = get_or_default(environ, "GOPATH")

debug = get_or_default(environ, "DEBUG")
