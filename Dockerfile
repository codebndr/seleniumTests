# Dockerfile to build container with Codebender selenium tests.

FROM ubuntu:12.04
# TODO: add MAINTAINER

# Install requirements and their dependencies
RUN apt-get update && apt-get install -y \
  libxml2-dev \
  libxslt1-dev \
  firefox \
  python3 \
  python3-dev \
  python3-setuptools

RUN easy_install3 pip
RUN pip install -U setuptools

# Add source code and install dependencies
RUN mkdir -p /opt/codebender
ADD . /opt/codebender/seleniumTests
WORKDIR /opt/codebender/seleniumTests
RUN pip3 install -r requirements-dev.txt

# Specify a default command for the container.
# Right now we simply run bash. TODO: add ENTRYPOINT for running tests.
WORKDIR /opt/codebender/seleniumTests
CMD ["/bin/bash"]
