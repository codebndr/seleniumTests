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

    parser.addoption("-S", "--source", action="store", default=config.SOURCE_BACHELOR,
                     help="Indicate the source used to generate the repo. "
                          "By default, we assume `bachelor`. "
                          "You can instead use `codebender_cc` for the live site.")

    parser.addoption("-C", "--capabilities", action="store",
                     default=config.DEFAULT_CAPABILITIES_FILE_PATH,
                     help="Custom path to a YAML file containing a capability list.")

    parser.addoption("-P", "--plugin", action="store_true",
                     default=False,
                     help="Install plugin in Firefox profile")


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


@pytest.fixture(autouse=True)
def requires_extension(request, webdriver):
    """Mark that a test requires the codebender extension.
    Ideally, this marker would not be necessary. However, it is used so that we
    skip tests when running under chrome that require the extension (for now).
    This is due to the fact that the chrome driver leaves open the
    "confirm extension" dialogue without actually installing it.

     This functionality should be invoked as a pytest marker, e.g.:

    ```
    @pytest.mark.requires_extension
    def test_some_feature():
        ...
    ```
    """
    if request.node.get_marker('requires_extension'):
        if webdriver.desired_capabilities["browserName"] == "chrome":
            pytest.skip("skipped test that requires codebender extension. "
                        "The current webdriver is Chrome, and the ChromeDriver "
                        "does not properly install extensions.")