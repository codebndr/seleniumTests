# Dockerfile to build container with Codebender selenium tests.

FROM ubuntu:14.04
# TODO: add MAINTAINER

# Install requirements and their dependencies
RUN apt-get update -y
RUN apt-get install -y \
  gcc \
  libffi-dev \
  python \
  python-dev \
  python-setuptools \
  openssl \
  libssl-dev \
  mailutils \
  ssmtp \
  sharutils

RUN easy_install pip
RUN pip install --upgrade pip
#RUN pip install -U setuptools

# Add source code and install dependencies
RUN mkdir -p /opt/codebender
ADD . /opt/codebender/seleniumTests

WORKDIR /opt/codebender/seleniumTests

RUN pip install -r requirements.txt

COPY ssmtp.conf /etc/ssmtp/

# Specify a default command for the container.
# Right now we simply run bash. TODO: add ENTRYPOINT for running tests.

#CMD ["/bin/bash"]
