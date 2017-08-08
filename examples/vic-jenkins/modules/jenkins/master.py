import os
from pprint import pprint

from docker import DockerClient
from jenkinsapi.credential import SSHKeyCredential
from jenkinsapi.jenkins import Jenkins

import govc
from modules import vicmachine
from modules.jenkins import slave, utils

JOB_NAME = "vic-engine"

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
            print("Deleting existing credentials.")
            del creds[utils.CREDS_DESCRIPTION]

        print("Uploading new credentials")

        creds[utils.CREDS_DESCRIPTION] = SSHKeyCredential(cred_dict)

        xml = config_template.format(**settings.integration_esx_settings)

        if JOB_NAME in jenkins:
            print("Updating job")
            job = jenkins[JOB_NAME]
            job.update_config(xml)
        else:
            print("Creating job")
            job = jenkins.create_job(jobname=JOB_NAME, xml=xml)

        pprint(job)

    else:
        print("Failed to find the container to configure.")
        return


config_template = """
    <flow-definition plugin="workflow-job@2.12.1">
        <actions>
            <org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction plugin="pipeline-model-definition@1.1.9">
                <jobProperties/>
                <triggers/>
                <parameters/>
            </org.jenkinsci.plugins.pipeline.modeldefinition.actions.DeclarativeJobPropertyTrackerAction>
        </actions>
        <description/>
        <keepDependencies>false</keepDependencies>
        <properties>
        <org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty/>
        <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
            <triggers/>
        </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
        </properties>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.37">
            <script>
pipeline {{
    agent {{ label 'slave' }}   

    environment {{
        PY_BOT_ARGS = '--exclude bugs'
        GOPATH = '/var/jenkins_home/gopath'
        GOROOT = '/usr/local/go'
        VIC_MACHINE_PATH = '${{WORKSPACE}}/bin/vic-machine-linux'
        DOCKER_FLAGS = '-H tcp://localhost:2376'
        DRONE_BUILD_NUMBER="0"
        GITHUB_AUTOMATION_API_KEY = '{GITHUB_AUTOMATION_API_KEY}'
        TEST_USERNAME = '{TEST_USERNAME}'
        TEST_PASSWORD = '{TEST_PASSWORD}'
        TEST_DATASTORE = "{TEST_DATASTORE}"
        TEST_TIMEOUT = "1800s"
        PUBLIC_NETWORK = "{PUBLIC_NETWORK}"
        BRIDGE_NETWORK = "{BRIDGE_NETWORK}"
        CONTAINER_NETWORK = "{CONTAINER_NETWORK}"
        MANAGEMENT_NETWORK = "{MANAGEMENT_NETWORK}"
        DOMAIN = "{DOMAIN}"
        ESX_HOST_0 = "{ESX_HOST_0}"
    }}

    stages {{
        stage('Prepare') {{
            steps {{
                sh 'rm -f *.zip log.html'
            }}
        }}
    
        stage('Clone') {{
            steps {{
                git url: 'https://github.com/Alphasite/vic'
                sh 'mkdir -p $GOPATH/src/github.com/vmware/vic'
                sh 'mount --bind . $GOPATH/src/github.com/vmware/vic'
            }}
        }}
        
        stage('Build') {{ 
            steps {{
                parallel(
                    vicmachine: {{ 
                        sh 'docker $DOCKER_FLAGS run -v $GOPATH:/go  -w /go/src/github.com/vmware/vic -e BUILD_NUMBER=10000 golang:1.8 make vic-machine' 
                    }},
                    appliance: {{ 
                        sh 'docker $DOCKER_FLAGS run -v $GOPATH:/go  -w /go/src/github.com/vmware/vic -e BUILD_NUMBER=10000 golang:1.8 make appliance'
                    }},
                    boostrap: {{ 
                        sh 'docker $DOCKER_FLAGS run -v $GOPATH:/go  -w /go/src/github.com/vmware/vic -e BUILD_NUMBER=10000 golang:1.8 make bootstrap' 
                    }},
                )
            }}
        }}
        
        stage('Test') {{
            steps {{
                parallel(
                        Unit_Test: {{
                            sh 'docker -H tcp://localhost:2376 run -v $GOPATH:/go  -w /go/src/github.com/vmware/vic -e BUILD_NUMBER=10000 golang:1.8 make test'
                        }},
                        Integration_Test: {{
                            sh 'bash -x examples/vic-jenkins/vic-test/init_test.bash tests/integration-test.sh full ci'
                        }},
                )
            }}
        }}
       
        // stage('Deploy') {{ 
        //     steps {{ 
        //         sh 'pip3 install -r examples/vic-jenkins/requirements.txt'
        //         sh 'cd examples/vic-jenkins; python3 run.py create vch' 
        //     }}
        // }}                        
    }}
    
    post {{
       success {{
          archive "log.html"
          archive "*-container-logs.zip.zip"
          archive "*-certs.zip"
       }}
    }}
}}
            </script>
            <sandbox>true</sandbox>
        </definition>
        <triggers/>
        <disabled>false</disabled>
    </flow-definition>
"""
