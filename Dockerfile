# Dockerfile to build container with Codebender selenium tests.

FROM ubuntu:12.04
# TODO: add MAINTAINER

# Install requirements and their dependencies
RUN apt-get update && apt-get install -y \
  python \
  python-setuptools

RUN easy_install pip
RUN pip install -U setuptools

# Add source code and install dependencies
RUN mkdir -p /opt/codebender
ADD . /opt/codebender/seleniumTests
WORKDIR /opt/codebender/seleniumTests
RUN pip install -r requirements-dev.txt

# Specify a default command for the container.
# Right now we simply run bash. TODO: add ENTRYPOINT for running tests.
WORKDIR /opt/codebender/seleniumTests
CMD ["/bin/bash"]
