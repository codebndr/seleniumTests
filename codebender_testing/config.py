import os

from selenium import webdriver


# URL of the site to be used for testing
BASE_URL = "http://localhost"

# URL of the actual Codebender website
LIVE_SITE_URL = "http://codebender.cc"

_EXTENSIONS_DIR = 'extensions'
_FIREFOX_EXTENSION_FNAME = 'codebender.xpi'

# Files used for testing
TEST_DATA_DIR = 'test_data'
TEST_DATA_BLANK_PROJECT = os.path.join(TEST_DATA_DIR, 'blank_project.ino')

# Set up Selenium Webdrivers to be used for selenium tests

def _get_firefox_profile():
    """Returns the Firefox profile to be used for the FF webdriver.
    Specifically, we're equipping the webdriver with the Codebender
    extension.
    """
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.add_extension(
        extension=os.path.join(_EXTENSIONS_DIR, _FIREFOX_EXTENSION_FNAME)
    )
    return firefox_profile

WEBDRIVERS = {
    "firefox": webdriver.Firefox(firefox_profile=_get_firefox_profile())
}

# Credentials to use when logging into the site via selenium
TEST_CREDENTIALS = {
    "username": "tester",
    "password": "testerPASS"
}

TEST_PROJECT_NAME = "test_project"

# How long we wait until giving up on trying to locate an element
ELEMENT_FIND_TIMEOUT = 5
