from time import gmtime
from time import strftime
import json
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import pytest

from codebender_testing.config import BASE_URL
from codebender_testing.config import ELEMENT_FIND_TIMEOUT
from codebender_testing.config import TEST_CREDENTIALS
from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.config import WEBDRIVERS


# Time to wait until we give up on a DOM property becoming available.
DOM_PROPERTY_DEFINED_TIMEOUT = 10

# JavaScript snippet to extract all the links to sketches on the current page.
# `selector` is a CSS selector selecting these links.
_GET_SKETCHES_SCRIPT = \
    "return $('{selector}').map(function() {{ return this.href; }}).toArray();"

# JavaScript snippet to verify the code on the current page.
_VERIFY_SCRIPT = "compilerflasher.verify()"

# How long (in seconds) to wait before assuming that an example
# has failed to compile
VERIFY_TIMEOUT = 15

# Messages displayed to the user after verifying a sketch.
VERIFICATION_SUCCESSFUL_MESSAGE = "Verification Successful"
VERIFICATION_FAILED_MESSAGE = "Verification failed."

class SeleniumTestCase(object):
    """Base class for all Selenium tests."""

    # This can be configured on a per-test case basis to use a different
    # URL for testing; e.g., http://localhost, or http://codebender.cc
    site_url = BASE_URL

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
        if re.match(".+?://", url):
            # url specifies an absolute path.
            return self.driver.get(url)
        else:
            url = url.lstrip('/')
            return self.driver.get("%s/%s" % (self.site_url, url))

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
            expected_conditions.visibility_of_element_located(locator))
        return self.driver.find_element(*locator)

    def delete_project(self, project_name):
        """Deletes the project specified by `project_name`. Note that this will
        navigate to the user's homepage."""
        self.open('/')
        created_project = self.get_element(By.LINK_TEXT, project_name)
        delete_button_li = created_project.find_element_by_xpath('..')
        delete_button = delete_button_li.find_element_by_css_selector('button:last-child')
        delete_button.click()
        popup_delete_button = self.get_element(By.ID, 'deleteProjectButton')
        popup_delete_button.click()

    def compile_sketch(self, url, iframe=False):
        """Compiles the sketch located at `url`, or an iframe within the page
        referred to by `url`.  Raises an exception if it does not compile.
        Note: this was written for the live site, and probably does not work
        with the bachelor version due to CSS / JS changes.
        """
        self.open(url)
        if iframe:
            # Note: here, we simply get the first iframe on the page.
            # There's a slightly less awkward way to do this that involves
            # giving this iframe a meaningful name in the HTML (TODO?)
            self.driver.switch_to_frame(0)
        self.execute_script(_VERIFY_SCRIPT)
        compile_result = WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            any_text_to_be_present_in_element((By.ID, "cb_cf_operation_output"),
                VERIFICATION_SUCCESSFUL_MESSAGE, VERIFICATION_FAILED_MESSAGE))
        if compile_result != VERIFICATION_SUCCESSFUL_MESSAGE:
            raise VerificationError(compile_result)


    def compile_all_sketches(self, url, selector, iframe=False, log_file=None):
        """Compiles all projects on the page at `url`. `selector` is a CSS selector
        that should select all relevant <a> tags containing links to sketches.
        `log_file` specifies a path to a file to which test results will be
        logged. If it is not `None`, compile errors will not cause the test
        to halt, but rather be logged to the given file. `log_file` may be a time
        format string, which will be formatted appropriately.
        `iframe` specifies whether the urls pointed to by `selector` are contained
        within an iframe.
        """
        self.open(url)
        sketches = self.execute_script(_GET_SKETCHES_SCRIPT.format(selector=selector))
        assert len(sketches) > 0

        if log_file is None:
            for sketch in sketches:
                self.compile_sketch(sketch, iframe=iframe)
        else:
            log_entry = {'succeeded': [], 'failed': []}
            for sketch in sketches:
                try:
                    self.compile_sketch(sketch, iframe=iframe)
                    log_entry['succeeded'].append(sketch)
                except (VerificationError, WebDriverException) as e:
                    log_entry['failed'].append({
                        'sketch': sketch,
                        'exception': "%s; %s" % (type(e).__name__, str(e))
                        # TODO?: is it possible to get the actual compiler error?
                    })
            # Dump the test results to `log_file`.
            f = open(strftime(log_file, gmtime()), 'w')
            json.dump(log_entry, f)
            f.close()


    def execute_script(self, script, *deps):
        """Waits for all JavaScript variables in `deps` to be defined, then
        executes the given script. Especially useful for waiting for things like
        jQuery to become available for use."""
        if len(deps) > 0:
            WebDriverWait(self.driver, DOM_PROPERTY_DEFINED_TIMEOUT).until(
                dom_properties_defined(*deps))
        return self.driver.execute_script(script)


class VerificationError(Exception):
    """An exception representing a failed verification of a sketch."""
    pass


class dom_properties_defined(object):
    """An expectation for the given DOM properties to be defined.
    See selenium.webdriver.support.expected_conditions for more on how this
    type of class works.
    """

    def __init__(self, *properties):
        self._properties = properties

    def __call__(self, driver):
        return all(
            driver.execute_script("return window.%s !== undefined" % prop)
            for prop in self._properties)


class any_text_to_be_present_in_element(object):
    """An expectation for checking if any of the given strings are present in
    the specified element. Returns the string that was present.
    """
    def __init__(self, locator, *texts):
        self.locator = locator
        self.texts = texts

    def __call__(self, driver):
        try :
            element_text = expected_conditions._find_element(driver, self.locator).text
            for text in self.texts:
                if text in element_text:
                    return text
            return False
        except StaleElementReferenceException:
            return False
