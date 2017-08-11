# Docker Compose Approach

First generate your ssh key into the `jenkins-ssh-keys` folder.

```
docker-compose build
docker-compose push
DOCKER_TLS_VERIFY=1 DOCKER_CERT_PATH=./jenkins-vch-2 DOCKER_HOST=sc-rdops-vm08-dhcp-244-158.eng.vmware.com:2376 COMPOSE_TLS_VERSION="TLSv1_2" docker-compose up -d
source venv/bin/activate 
python run.py jenkins master configure
python run.py jenkins slave configure
```