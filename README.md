# Codebender Selenium Tests

This repo contains Selenium tests for the codebender website.  The tests are
written in Python 2, and utilize pytest as a testing framework and Selenium
for browser automation.

## Running Tests

Tests are run by invoking `tox`. Run `tox --help` to see all the
Codebender-specific arguments that can be passed to `py.test`.

In addition to these arguments, there are certain environment variables that
should be set when running tests:

- `CODEBENDER_SELENIUM_HUB_URL`: the URL of the Selenium Hub. If you are using
  SauceLabs, the URL has the following format:
  `http://{USERNAME}:{ACCESS_KEY}@ondemand.saucelabs.com:80/wd/hub`. You can
  also use a [docker-selenium](https://github.com/SeleniumHQ/docker-selenium)
  hub. In that case, it is necessary to link the docker-selenium instance to the
  Docker instance from which tests are running.
- `CODEBENDER_TEST_USER`: username that the webdriver will use to log into the
  site in order to perform tests.
- `CODEBENDER_TEST_PASS`: password for `CODEBENDER_TEST_USER`.

Rather than invoking `tox` directly, the easiest way to run tests is with
Docker. If you are not familiar with Docker, please consult the
[documentation](http://docs.docker.com/) for an introduction.

First, build the image with `$ docker build . -t codebender/selenium`.

Then invoke `tox` via `docker run`. Here is a sample command to run all tests,
where the Codebender server is running at `http://192.168.1.2:8080`:

```
$ docker run -e CODEBENDER_SELENIUM_HUB_URL=http://johndoe:12345678-1234-1234-1234-12345678910@ondemand.saucelabs.com:80/wd/hub \
             -e CODEBENDER_TEST_USER=tester \
             -e CODEBENDER_TEST_PASS=1234 \
             -it codebender/selenium \
             tox -- --url http://192.168.1.2:8080 --source bachelor
```

### Running Tests Manually

The recommended way of running tests is with Docker. If you would like to
manually provision your machine to be able to run tests, you can use the
Dockerfile as a step-by-step guide for provisioning. Then invoke `tox` to run
tests.

#### Specifying a URL for Tests

Tests can either be run for the
[bachelor](https://github.com/codebendercc/bachelor) version of the site,
running locally, or for the live site. The version of the site that is running
is inferred from the `--url` parameter. You can run `$ tox --url
http://localhost` to run the tests for a locally running bachelor site (this is
the default url), or `$ tox --url http://codebender.cc` to run the tests for the
live site.

Certain tests are specially written for one site or the other. This is
implemented with a custom `pytest` marker. Tests that require a certain `--url`
are decorated with `@pytest.mark.requires_url(<url>)`.

### Changing Test Configuration

Various global configuration parameters are specified in
`codebender_testing/config.py`.  Such parameters include URLs and site endpoints
which are subject to change.  This is also where the webdrivers (Firefox and
Chrome) are specified.

## Compilation Logs

Certain tests exist to iterate through groups of sketches and compile them
one-by-one.  Since these tests take a long time, they are not run in full by
default. You can run them by specifying the `--full` option; for example: `$ tox
tests/cb_compile_tester --full`.

The following test cases are compile tests that generate such logs:
- `tests/libraries/test_libraries.py::TestLibraryExamples`
- `tests/compile_tester/test_compile_tester_projects.py::TestCompileTester`

The generated logs are placed in the `logs` directory. They give detailed output
in JSON format containing the codebender site URL that was used to run the
tests, along with the URLs of the individual sketches that were compiled, and
whether they succeeded or failed to compile.

## Framework Overview

The following outlines the structure of the repository as well as important
framework components.

### Directory Structure

#### `tests/`

The `tests/` directory contains all of the actual unit tests for the codebender
site. That is, all of the tests discovered by `py.test` should come from this
directory.

**`tests/conftest.py`** contains the global configuration for pytest,
including specifying the webdriver fixtures as well as the available command
line arguments.

#### `codebender_testing/`

This is where all major components of the testing framework live. All of the
unit tests rely on the files in this directory.

**`codebender_testing/config.py`** specifies global configuration parameters for
testing (see "Changing Test Configuration" above).

**`codebender_testing/utils.py`** defines codebender-specific utilities used to
test the site. These mostly consist of abstractions to the Selenium framework.
The most important class is `SeleniumTestCase`, which all of the unit test cases
inherit from. This grants them access (via `self`) to a number of methods and
attributes that are useful for performing codebender-specific actions.

**`codebender_testing/capabilities_{firefox, chrome}.yaml`** defines a list of `capabilities` to
be passed as arguments when instantiating remote webdrivers. In particular, it
specifies the web browsers that we would like to use. Consult this file for more
information.

#### `batch/`

The `batch/` directory contains any executable scripts not directly used to
perform tests. For example, it contains a script `fetch_projects.py` which can
be used to download all of the public projects of a particular codebender user.

#### `extensions/`

The `extensions/` directory contains the codebender browser extensions to be
used by the Selenium webdrivers.

#### `test_data/`

The `test_data/` directory contains any data used for testing. For example, it
contains example projects that we should successfully be able to upload and
compile.

#### `logs/`

The `logs/` directory contains the results of running certain tests, e.g.
whether certain sets of sketches have compiled successfully (see "Compilation
Logs").
