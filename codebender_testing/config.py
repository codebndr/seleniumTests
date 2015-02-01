from selenium import webdriver


BASE_URL = "http://localhost"

WEBDRIVERS = {
    "firefox": webdriver.Firefox,
    "chrome": webdriver.Chrome
}

TEST_CREDENTIALS = {
    "username": "tester",
    "password": "testerPASS"
}
