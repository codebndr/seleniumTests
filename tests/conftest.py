import pytest

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

