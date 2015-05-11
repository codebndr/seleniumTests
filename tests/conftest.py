import pytest

from codebender_testing.config import BASE_URL
from codebender_testing.config import WEBDRIVERS


@pytest.fixture(scope="session", params=WEBDRIVERS.keys())
def webdriver(request):
    """Returns a webdriver that persists across the entire test session,
    and registers a finalizer to close the browser once the session is
    complete. The entire test session is repeated once per driver.
    """
    driver = WEBDRIVERS[request.param]
    request.addfinalizer(lambda: driver.quit())
    return driver

def pytest_addoption(parser):
    """Adds command line options to py.test."""
    parser.addoption("--url", action="store", default=BASE_URL,
                     help="URL to use for testing, e.g. http://localhost, http://codebender.cc")

@pytest.fixture(scope="class")
def testing_url(request):
    return request.config.getoption("--url")

@pytest.fixture(autouse=True)
def skip_by_site(request, testing_url):
    """Skips tests that require a certain site URL in order to run properly."""
    if request.node.get_marker('requires_url'):
        required_url = request.node.get_marker('requires_url').args[0]
        if required_url.rstrip('/') != testing_url.rstrip('/'):
            pytest.skip('skipped test that requires --url=%s')

