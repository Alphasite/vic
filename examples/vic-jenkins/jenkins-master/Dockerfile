FROM jenkins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

RUN echo 2.0 > /usr/share/jenkins/ref/jenkins.install.UpgradeWizard.state

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y \
 && DEBIAN_FRONTEND=noninteractive apt-get -yy -q install \
    curl \
    apt-transport-https \
    software-properties-common \
    ca-certificates \
    gnupg2

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
 && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
 && DEBIAN_FRONTEND=noninteractive apt-get update -y \
 && DEBIAN_FRONTEND=noninteractive apt-get -yy -q install docker-ce