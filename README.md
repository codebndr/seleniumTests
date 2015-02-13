# Codebender Selenium Tests

This repo contains Selenium tests for the codebender website.
The tests are written in Python 3.

## Running Tests

To run tests locally, you'll need to be running a selenium server. See
[here](https://selenium-python.readthedocs.org/installation.html#downloading-selenium-server)
for instructions.

Once you've got a Selenium server running, simply run `$ tox` from within the
repo. If you don't have tox, run `$ sudo pip3 install -r requirements-dev.txt`
from within the repo to install it.

When running tox, you might get a `pkg_resources.DistributionNotFound` error
with reference to `virtualenv`. This is likely due to an out of date setuptools.
To fix this issue, run `$ sudo pip3 install -U setuptools`.
