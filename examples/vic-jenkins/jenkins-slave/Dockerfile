# Adds vim and net-tools (for ifconfig) - once you have a shell, you often want these
# After deployment, you can use docker exec to configure sshd.
#
# - Add a user and/or public key. Script will create the user if it doesn't exist
# docker exec -d myContainer /usr/bin/adduserkey derek "$(cat /home/derek/.ssh/id_rsa.pub)"
#
# - Set a password
# docker exec -d myContainer /usr/sbin/usermod --password $(echo foobar | openssl passwd -1 -stdin) root

FROM bensdoings/dind-debian

RUN DEBIAN_FRONTEND=noninteractive apt-get -yy -q install \
    net-tools \
    vim \
    openssh-server \
    sudo \
    && mkdir /var/run/sshd && chmod 700 /var/run/sshd

RUN echo "deb http://http.debian.net/debian jessie-backports main" | \
    sudo tee --append /etc/apt/sources.list.d/jessie-backports.list > /dev/null

RUN apt update -y \
 && apt install --target-release jessie-backports \
          openjdk-8-jre-headless \
          ca-certificates-java \
          --assume-yes

RUN DEBIAN_FRONTEND=noninteractive apt install -y --target-release jessie-backports \
    python3 \
    golang-go \
    python3-pip

RUN pip3 install robotframework

RUN DEBIAN_FRONTEND=noninteractive apt install -y --target-release jessie-backports \
    make \
    git

RUN curl -o go.tar.gz https://storage.googleapis.com/golang/go1.8.3.linux-amd64.tar.gz \
 && tar -C /usr/local -xzf go.tar.gz

ENV PATH /usr/local/go/bin:$PATH
ENV GOROOT /usr/local/go

# Uncomment to add a default user to the image
RUN useradd -s /bin/bash -m -p $(openssl passwd -1 jenkins) jenkins \
 && su jenkins && mkdir ~/.ssh && chmod 700 ~/.ssh \
 && echo "jenkins   ALL=(ALL:ALL) ALL" >> /etc/sudoers

RUN ln -s /usr/bin/java /bin/java

EXPOSE 2376 22

CMD [ "/etc/rc.local" ]

COPY rc.local /etc
COPY adduserkey /usr/bin

COPY config/authorized_keys /root/.ssh/authorized_keys
COPY config/daemon.json /etc/docker/daemon.json

VOLUME /var/jenkins_home

