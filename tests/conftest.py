"""The configuration file for `py.test`.

This file specifies global test fixtures, which include the selenium
webdrivers.

This is also where command-line arguments and pytest markers are defined.
"""

import os
import sys

import pytest

from codebender_testing import config


def pytest_addoption(parser):
    """Adds command line options to the testing suite."""

    parser.addoption("--url", action="store", default=config.BASE_URL,
                     help="URL to use for testing, e.g. http://localhost, http://codebender.cc")

    parser.addoption("--full", action="store_true", default=False,
                     help="Run the complete set of compile tests (a minimal set of tests is run by default).")

    parser.addoption("--source", action="store", default=config.SOURCE_BACHELOR,
                     help="Indicate the source used to generate the repo. "
                          "By default, we assume `bachelor`.")


@pytest.fixture(scope="session", params=config.get_browsers())
def webdriver(request):
    """Returns a webdriver that persists across the entire test session,
    and registers a finalizer to close the browser once the session is
    complete. The entire test session is repeated once per driver.
    """

    # TODO: maybe have a different way of specifying this (?)
    command_executor = os.environ['CODEBENDER_SELENIUM_HUB_URL']
    desired_capabilities = request.param

    driver = config.create_webdriver(command_executor, desired_capabilities)

    # TODO: update sauce status via SauceClient, but only if the command_executor
    # is a sauce URL.
    def finalizer():
        # print("Link to your job: https://saucelabs.com/jobs/%s" % driver.session_id)
        try:
            pass
            # TODO:
            # if sys.exc_info() == (None, None, None):
            #     sauce.jobs.update_job(driver.session_id, passed=True)
            # else:
            #     sauce.jobs.update_job(driver.session_id, passed=False)
        finally:
            driver.quit()

    request.addfinalizer(finalizer)
    return driver


@pytest.fixture(scope="class")
def testing_url(request):
    """A fixture to get the --url parameter."""
    return request.config.getoption("--url")


@pytest.fixture(scope="class")
def source(request):
    """A fixture to specify the source repository from which the site was
    derived (e.g. bachelor or codebender_cc)
    """
    return request.config.getoption("--source")


@pytest.fixture(scope="class")
def testing_credentials(request):
    """A fixture to get testing credentials specified via the environment
    variables CODEBENDER_TEST_USER and CODEBENDER_TEST_PASS. Defaults to the
    credentials specified in config.TEST_CREDENTIALS.
    """
    return {
        'username': os.environ.get('CODEBENDER_TEST_USER', config.TEST_CREDENTIALS['username']),
        'password': os.environ.get('CODEBENDER_TEST_PASS', config.TEST_CREDENTIALS['password']),
    }


@pytest.fixture(scope="class")
def testing_full(request):
    """A fixture to get the --full parameter."""
    return request.config.getoption("--full")


@pytest.fixture(autouse=True)
def requires_source(request, source):
    """Skips tests that require a certain source version (e.g. bachelor or
    codebender_cc) in order to run properly.

    This functionality should be invoked as a pytest marker, e.g.:

    ```
    @pytest.mark.requires_source("bachelor")
    def test_some_feature():
        ...
    ```
    """
    if request.node.get_marker('requires_source'):
        required_source = request.node.get_marker('requires_source').args[0]
        if required_source != source:
            pytest.skip('skipped test that requires --source=' + source)


@pytest.fixture(autouse=True)
def requires_url(request, testing_url):
    """Skips tests that require a certain site URL in order to run properly.
    This is strictly more specific than skip_by_source; consider using that
    marker instead.

    This functionality should be invoked as a pytest marker, e.g.:

    ```
    @pytest.mark.requires_url("http://codebender.cc")
    def test_some_feature():
        ...
    ```
    """
    if request.node.get_marker('requires_url'):
        required_url = request.node.get_marker('requires_url').args[0]
        if required_url.rstrip('/') != testing_url.rstrip('/'):
            pytest.skip('skipped test that requires --url=%s' % required_url)
