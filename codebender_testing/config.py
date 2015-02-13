from selenium import webdriver


# URL of the site to be used for testing
BASE_URL = "http://localhost"

# Selenium Webdrivers to be used for selenium tests
WEBDRIVERS = {
    "firefox": webdriver.Firefox
}

# Credentials to use when logging into the site via selenium
TEST_CREDENTIALS = {
    "username": "tester",
    "password": "testerPASS"
}

TEST_PROJECT_NAME = "test_project"

# How long we wait until giving up on trying to locate an element
ELEMENT_FIND_TIMEOUT = 5
