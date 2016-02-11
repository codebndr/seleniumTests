"""The configuration file for `py.test`.

This file specifies global test fixtures, which include the selenium
webdrivers.

This is also where command-line arguments and pytest markers are defined.
"""

import os
import shutil

import pytest

from codebender_testing import config


def pytest_addoption(parser):
    """Adds command line options to the testing suite."""

    parser.addoption("-U", "--url", action="store", default=config.BASE_URL,
                     help="URL to use for testing, e.g. http://localhost, http://codebender.cc")

    parser.addoption("-F", "--full", action="store_true", default=False,
                     help="Run the complete set of compile tests "
                          "(a minimal set of tests is run by default).")

    parser.addoption("-C", "--capabilities", action="store",
                     default=config.DEFAULT_CAPABILITIES_FILE_PATH,
                     help="Custom path to a YAML file containing a capability list.")

    parser.addoption("-P", "--plugin", action="store_true",
                     default=False,
                     help="Install plugin in Firefox profile")

    parser.addoption("-L", "--libraries", action="store",
                     default='',
                     help="Target libraries to test")


def pytest_generate_tests(metafunc):
    """Special function used by pytest to configure test generation."""

    # Paremetrize the desired_capabilities fixture on each of the capabilities
    # objects in the YAML file.
    if 'desired_capabilities' in metafunc.fixturenames:
        capabilities_path = metafunc.config.option.capabilities
        metafunc.parametrize('desired_capabilities',
                             config.get_browsers(capabilities_path),
                             scope="session")


@pytest.fixture(scope="session")
def webdriver(request, desired_capabilities):
    """Returns a webdriver that persists across the entire test session,
    and registers a finalizer to close the browser once the session is
    complete. The entire test session is repeated once per driver.
    """

    command_executor = os.environ['CODEBENDER_SELENIUM_HUB_URL']

    webdriver = config.create_webdriver(command_executor, desired_capabilities)
    driver = webdriver['driver']
    driver.maximize_window()
    profile_path = webdriver['profile_path']

    def finalizer():
        try:
            driver.quit()
        finally:
            if profile_path and os.path.exists(profile_path):
                print '\n\nRemoving browser profile directory:', profile_path
                shutil.rmtree(profile_path, ignore_errors=True)

    request.addfinalizer(finalizer)
    return driver


@pytest.fixture(scope="class")
def testing_url(request):
    """A fixture to get the --url parameter."""
    return request.config.getoption("--url")

@pytest.fixture(scope="class")
def testing_credentials(request):
    """A fixture to get testing credentials specified via the environment
    variables CODEBENDER_TEST_USER and CODEBENDER_TEST_PASS.
    """
    return {
        'username': os.environ.get('CODEBENDER_TEST_USER'),
        'password': os.environ.get('CODEBENDER_TEST_PASS'),
    }


@pytest.fixture(scope="class")
def testing_full(request):
    """A fixture to get the --full parameter."""
    return request.config.getoption("--full")

@pytest.fixture(autouse=True)
def requires_url(request, testing_url):
    """Skips tests that require a certain site URL in order to run properly.
    This is strictly more specific than requires_source; consider using that
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
