# Dockerfile to build container with Codebender selenium tests.

FROM ubuntu:12.04
# TODO: add maintainer.

# Install Python and necessary utilities
RUN apt-get update
RUN apt-get install -y python3 python3-setuptools
RUN apt-get clean
RUN easy_install3 pip

# Add source code and install dependencies
RUN mkdir -p /opt/codebender
ADD . /opt/codebender/seleniumTests
WORKDIR /opt/codebender/seleniumTests
RUN ls -l
RUN pip3 install -r requirements-dev.txt

# Specify a default command for the container.
# Right now we simply run ls. TODO: run tests.
WORKDIR /opt/codebender/seleniumTests
CMD ["ls", "-l"]

