# Dockerfile to build container with Codebender selenium tests.

FROM ubuntu:12.04
# TODO: add MAINTAINER

# Install minimal dev utilities
RUN apt-get update
RUN apt-get install -y git vim

# Install Python and necessary utilities
RUN apt-get install -y python3 python3-setuptools
RUN easy_install3 pip
RUN pip install -U setuptools

# Install web browsers for local testing
RUN apt-get install -y firefox

# Cleanup
RUN apt-get clean

# Add source code and install dependencies
RUN mkdir -p /opt/codebender
ADD . /opt/codebender/seleniumTests
WORKDIR /opt/codebender/seleniumTests
RUN pip3 install -r requirements-dev.txt

# Specify a default command for the container.
# Right now we simply run bash. TODO: add ENTRYPOINT for running tests.
WORKDIR /opt/codebender/seleniumTests
CMD ["/bin/bash"]

