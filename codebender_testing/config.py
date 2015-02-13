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

# How long to wait before we give up on the 'verify' command (in seconds)
VERIFY_TIMEOUT = 10

