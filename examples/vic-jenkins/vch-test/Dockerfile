FROM buildpack-deps:buster-curl

RUN wget https://download.docker.com/linux/static/stable/x86_64/docker-17.06.0-ce.tgz \
 && tar xvzf docker-17.06.0-ce.tgz \
 && mkdir -p /test

CMD bash /test/test.bash

ADD test.bash /test