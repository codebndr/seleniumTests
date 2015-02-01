import re
import sys

from selenium import webdriver
import pytest

from codebender_testing.config import WEBDRIVERS
from codebender_testing.config import BASE_URL


class SeleniumTestCase(object):
    """Base class for all Selenium tests."""

    @classmethod
    @pytest.fixture(scope="class", autouse=True, params=WEBDRIVERS.keys())
    def setup(self, request):
        """Sets up attributes that should be accessible to all test cases."""

        # Repeat each test for each webdriver configuration
        webdriver_cls = WEBDRIVERS[request.param]
        self.driver = webdriver_cls()

    def open(self, url):
        """Open the resource specified by `url`.
        If an absolute URL is specified (like 'http://codebender.cc') we
        use that URL. Otherwise the resource is relative to `BASE_URL` in
        `codebender_testing.config`.
        """
        if re.match(".+?://^", url):
            return self.driver.get(url)
        else:
            return self.driver.get("%s/%s" % (BASE_URL, url))

