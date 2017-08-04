# Adds vim and net-tools (for ifconfig) - once you have a shell, you often want these
# After deployment, you can use docker exec to configure sshd.
#
# - Add a user and/or public key. Script will create the user if it doesn't exist
# docker exec -d myContainer /usr/bin/adduserkey derek "$(cat /home/derek/.ssh/id_rsa.pub)"
#
# - Set a password
# docker exec -d myContainer /usr/sbin/usermod --password $(echo foobar | openssl passwd -1 -stdin) root

FROM debian:stretch-backports

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

RUN DEBIAN_FRONTEND=noninteractive apt-get -yy -q install \
    net-tools \
    vim \
    openssh-server \
    sudo \
    openjdk-8-jre-headless \
    ca-certificates-java \
    python3.5 \
    golang-1.8 \
    python3-pip \
    make \
    git \
 && mkdir /var/run/sshd && chmod 700 /var/run/sshd

RUN pip3 install robotframework jenkinsapi docker requests urllib3

# Uncomment to add a default user to the image
RUN useradd -s /bin/bash -m -p $(openssl passwd -1 jenkins) jenkins \
 && su jenkins && mkdir ~/.ssh && chmod 700 ~/.ssh \
 && echo "jenkins   ALL=(ALL:ALL) ALL" >> /etc/sudoers \
 && echo "export PATH=/usr/local/go/bin:\$PATH" >> /etc/profile \
 && echo "export GOROOT=/usr/local/go" >> /etc/profile \
 && ln -s /usr/lib/go-1.8 /usr/lib/go

EXPOSE 2376 22

CMD [ "/etc/rc.local" ]

COPY rc.local /etc
COPY adduserkey /usr/bin

COPY config/authorized_keys /root/.ssh/authorized_keys
COPY config/daemon.json /etc/docker/daemon.json

VOLUME /var/jenkins_home
