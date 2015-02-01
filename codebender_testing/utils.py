import re
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pytest

from codebender_testing.config import BASE_URL
from codebender_testing.config import TEST_CREDENTIALS
from codebender_testing.config import WEBDRIVERS


class SeleniumTestCase(object):
    """Base class for all Selenium tests."""

    @classmethod
    @pytest.fixture(scope="class", autouse=True, params=WEBDRIVERS.keys())
    def setup(self, request):
        """Sets up attributes that should be accessible to all test cases."""

        # Repeat each test for each webdriver configuration
        webdriver_cls = WEBDRIVERS[request.param]
        self.driver = webdriver_cls()

    def open(self, url=None):
        """Open the resource specified by `url`.
        If an absolute URL is specified (like 'http://codebender.cc') we
        use that URL. Otherwise the resource is relative to `BASE_URL` in
        `codebender_testing.config`.
        """
        if url is None:
            url = ''
        if re.match(".+?://^", url):
            # url specifies an absolute path.
            return self.driver.get(url)
        else:
            url = url.lstrip('/')
            return self.driver.get("%s/%s" % (BASE_URL, url))


def logged_in(func):
    """Decorator to ensure the user is logged in before performing a test.
    If not logged in, a login will be performed."""
    def inner(*args, **kwargs):
        test = args[0]
        try:
            test.open()
            login_button = test.driver.find_element_by_id('login_btn')
            login_button.send_keys(Keys.ENTER)
            # Enter credentials and log in
            user_field = test.driver.find_element_by_id('username')
            user_field.send_keys(TEST_CREDENTIALS['username'])
            pass_field = test.driver.find_element_by_id('password')
            pass_field.send_keys(TEST_CREDENTIALS['password'])
            do_login = test.driver.find_element_by_id('_submit')
            do_login.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # 'Log In' is not displayed, so we're already logged in.
            pass
        return func(*args, **kwargs)
    return inner

