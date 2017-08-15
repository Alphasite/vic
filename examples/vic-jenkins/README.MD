# Examples

## Deploying a VCH
```bash
python run.py vic.configure_firewall+deploy
```

## Deploying a Jenkins CI-CD system
### Docker Compose Approach

First generate your ssh key into the `jenkins-ssh-keys` folder.

```
source venv/bin/activate 
python run.py vic.deploy
python run.py jenkins.slave.prepare
docker-compose build
docker-compose push
DOCKER_TLS_VERIFY=1 DOCKER_CERT_PATH=./jenkins-vch-2 DOCKER_HOST=sc-rdops-vm08-dhcp-244-158.eng.vmware.com:2376 COMPOSE_TLS_VERSION="TLSv1_2" docker-compose up -d
python run.py jenkins.slave.configure
python run.py jenkins.master.configure
```

# Example `settings_local.py`

You need only populate the portions of the settings file which are relevant to you
any missing sections will cause an exception if needed and are ignored otherwise.

```python
import os

cwd = os.curdir
vic_dir = os.path.join(cwd, "..", "vic")

vic_build_dir = os.path.join("..", "vic-build-scripts")

vic_machine_path = os.path.join(vic_dir, "bin", "vic-machine-darwin")

esx_url = "10.249.249.249"
esx_username = "Administrator@vsphere.local"
esx_password = "Admin!23"
esx_thumbprint = "30:D0:FB:EC:0E:56:27:36:78:15:56:27:36:78:15:A3:03:01:C2:3E"
esx_tls_cname = "*.eng.vmware.com"

esx_hosts = [
    "10.160.250.6",
    "10.160.228.59",
    "10.160.229.236",
    "10.160.228.122",
]

cluster_name = "Cluster"

vch_name = "jenkins-vch"

image_stores = [
    "vsanDatastore/jenkins/vch-imagestore",
]

volume_stores = [
    "vsanDatastore/jenkins/vch-volumestore:default",
    "vsanDatastore/jenkins/vch-volumestore:volumes",
    "nfs://10.27.27.27/store/jenkins?uid=0&gid=0:nfs-store"
]

registry_cas = [
    # os.path.join(vic_build_dir, "registry", "ca.cert"),
]

bridge_network = "bridge"
public_network = "vm-network"
container_network = "external"
management_network = ""

repository_url = "vm-harbour.nishadmathur.com"
repository_user = "admin"
repository_password = "Harbor12345"
repository_group = "jenkins"

gopath = "/Users/mathurn/Documents/Software/vmware/gopath"

insecure_repositories = [
    "vm-harbour.nishadmathur.com",
    "10.234.234.192",
]

jenkins_admin_username = "test"
jenkins_admin_password = "test"

datastore_name = "vsanDatastore"

debug = "1"

integration_esx_settings = {
    "TEST_USERNAME": "ci",
    "TEST_PASSWORD": 'Admin@23',
    "TEST_DATASTORE": "esxi.0-local-datastore-0",
    "PUBLIC_NETWORK": "public_network",
    "BRIDGE_NETWORK": "bridge_network",
    "DOMAIN": "eng.vmware.com",
    "ESX_HOST": "10.202.134.202",
    "ESX_THUMBPRINT": "19:7C:F3:85:E0:A8:DA:E5:CD:4B:85:E0:A8:DA:6D:B4:38:F8:F8:D6",
    "ESX_TLS_CNAME": "*.eng.vmware.com",
    "GITHUB_AUTOMATION_API_KEY": "8b3bddf4272814a42",
    "VCH_TEST_IMAGE": "alphasite/docker-test",
}
```