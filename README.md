# Codebender Selenium Tests

This repo contains Selenium tests for the codebender website.  The tests are
written in Python 3, and utilize pytest as a testing framework and Selenium
for browser automation.

## Running Tests

### Dependencies

To run these tests, you'll need to have Python 3 installed. In addition, it is
advantageous to have pip, a package manager for Python, in order to install
dependencies.

Notably, the pip2 (for Python 2) and pip3 (for Python 3) packages both attempt
to link `/usr/local/bin/pip` to the `pip2` or `pip3` executable, respectively.
To deal with this, you could explicitly type out `pip3` or `pip2` instead of
`pip` whenever you use pip via the command line. (It may be best to just remove
`/usr/local/bin/pip` entirely).

To install `pip` in Ubuntu, run `$ sudo apt-get install python3
python3-setuptools`, then `$ sudo easy_install3 pip`.

After getting set up with pip and cloning the seleniumTests repo, you should
make sure to install all the seleniumTests dependencies by `cd`ing to your local
clone of the repo and running `$ sudo pip3 install -r requirements-dev.txt`.

### Invoking Tests via `tox`

After installing dependencies, you should have the `tox` command available. To
run all of the tests, you can simply run `$ tox` from within the cloned repo.

You can also run individual tests by providing the appropriate directory or
filename as an argument, for example: `$ tox tests/sketch`.

Invoking tox will also run `flake8`, which is essentially a lint checker for
Python. It is best to fix any issues reported by `flake8` before committing
to the repo. It can be run on its own via the command `$ flake8`.

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

