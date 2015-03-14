import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import pytest

from codebender_testing.config import BASE_URL
from codebender_testing.config import ELEMENT_FIND_TIMEOUT
from codebender_testing.config import TEST_CREDENTIALS
from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.config import WEBDRIVERS


_TEST_INPUT_ID = "_cb_test_input"

# Creates an input into which we can upload files using Selenium.
_CREATE_INPUT_SCRIPT = """
var input = window.$('<input id="{input_id}" type="file" style="position: fixed">');
window.$('body').append(input);
""".format(input_id=_TEST_INPUT_ID)

# After the file is chosen via Selenium, this script moves the file object
# (in the DOM) to the Dropzone.
def _move_file_to_dropzone_script(dropzone_selector):
    return """
var fileInput = document.getElementById('{input_id}');
var file = fileInput.files[0];
var dropzone = Dropzone.forElement('{selector}');
dropzone.drop({{ dataTransfer: {{ files: [file] }} }});
""".format(input_id=_TEST_INPUT_ID, selector=dropzone_selector)

class SeleniumTestCase(object):
    """Base class for all Selenium tests."""

    def dropzone_upload(self, selector, fname):
        """Uploads a file specified by `fname` via the Dropzone within the
        element specified by `selector`. (Dropzone refers to Dropzone.js)
        """
        # Create an artificial file input.
        self.execute_script(_CREATE_INPUT_SCRIPT)
        test_input = self.get_element(By.ID, _TEST_INPUT_ID)
        test_input.send_keys(fname)
        self.execute_script(_move_file_to_dropzone_script(selector))
        import time
        time.sleep(10)

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def _testcase_attrs(cls, webdriver):
        """Sets up any class attributes to be used by any SeleniumTestCase.
        Here, we just store fixtures as class attributes. This allows us to avoid
        the pytest boilerplate of getting a fixture value, and instead just
        refer to the fixture as `self.<fixture>`.
        """
        cls.driver = webdriver

    @pytest.fixture(scope="class")
    def tester_login(self): 
        self.login()

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

    def open_project(self, project_name=None):
        """Opens the project specified by `name`, bringing the driver to the
        sketch view of that project. Opens the test project if `name` is
        unspecified. The driver must be logged in to use this function."""
        if project_name is None:
            project_name = TEST_PROJECT_NAME

        project_link = self.driver.find_element_by_link_text(project_name)
        project_link.send_keys(Keys.ENTER)

    def login(self):
        """Performs a login."""
        try:
            self.open()
            login_button = self.driver.find_element_by_id('login_btn')
            login_button.send_keys(Keys.ENTER)
            # Enter credentials and log in
            user_field = self.driver.find_element_by_id('username')
            user_field.send_keys(TEST_CREDENTIALS['username'])
            pass_field = self.driver.find_element_by_id('password')
            pass_field.send_keys(TEST_CREDENTIALS['password'])
            do_login = self.driver.find_element_by_id('_submit')
            do_login.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # 'Log In' is not displayed, so we're already logged in.
            pass

    def get_element(self, *locator):
        """Waits for an element specified by *locator (a tuple of
        (By.<something>, str)), then returns it if it is found."""
        WebDriverWait(self.driver, ELEMENT_FIND_TIMEOUT).until(
            expected_conditions.presence_of_element_located(locator))
        return self.driver.find_element(*locator)
        
