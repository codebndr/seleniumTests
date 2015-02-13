from selenium import webdriver


# URL of the site to be used for testing
BASE_URL = "http://localhost"

# Selenium Webdrivers to be used for selenium tests
WEBDRIVERS = {
    "firefox": webdriver.Firefox,
    "chrome": webdriver.Chrome
}

# Credentials to use when logging into the site via selenium
TEST_CREDENTIALS = {
    "username": "tester",
    "password": "testerPASS"
}

TEST_PROJECT_NAME = "test_project"

