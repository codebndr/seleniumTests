from contextlib import contextmanager
from time import gmtime
from time import strftime
import json
import os
import re
import shutil
import tempfile

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
_VERIFY_SCRIPT = """
if (window.compilerflasher !== undefined) {
    compilerflasher.verify();
} else {
    // BACHELOR
    verify();
}
"""

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

# How long (in seconds) to wait before assuming that an example
# has failed to compile
VERIFY_TIMEOUT = 15

# Messages displayed to the user after verifying a sketch.
VERIFICATION_SUCCESSFUL_MESSAGE = "Verification Successful"
VERIFICATION_FAILED_MESSAGE = "Verification failed."


@contextmanager
def temp_copy(fname):
    """Creates a temporary copy of the file `fname`.
    This is useful for testing features that derive certain properties
    from the filename, and we want a unique filename each time we run the
    test (in case, for example, there is leftover garbage from previous
    tests with the same name).
    """
    extension = fname.split('.')[-1]
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.%s' % extension) as copy:
        with open(fname, 'rb') as original:
            shutil.copyfileobj(original, copy)
        copy.flush()
        yield copy


class CodebenderSeleniumBot(object):
    """Contains various utilities for navigating the Codebender website."""

    # This can be configured on a per-test case basis to use a different
    # URL for testing; e.g., http://localhost, or http://codebender.cc.
    # It is set via command line option in _testcase_attrs (below)
    site_url = None

    def start(url=None, webdriver=None):
        """Create the selenium webdriver, operating on `url`. We can't do this
        in an __init__ method, otherwise py.test complains about
        SeleniumTestCase having an init method.
        The webdriver that is created is specified as a key into the WEBDRIVERS
        dict (in codebender_testing.config)
        """
        if webdriver is None:
            webdriver = WEBDRIVERS.keys()[0]
        self.driver = WEBDRIVERS[webdriver]()

        if url is None:
            url = BASE_URL
        self.site_url = url

    @classmethod
    @contextmanager
    def session(cls, **kwargs):
        """Start a new session with a new webdriver. Regardless of whether an
        exception is raised, the webdriver is guaranteed to quit.
        The keyword arguments should be interpreted as in `start`.

        Sample usage:

        ```
        with CodebenderSeleniumBot.session(url="localhost",
                                           webdriver="firefox") as bot:
            # The browser is now open
            bot.open("/")
            assert "Codebender" in bot.driver.title
        # The browser is now closed
        ```

        Test cases shouldn't need to use this method; it's mostly useful for
        scripts, automation, etc.
        """
        try:
            bot = cls()
            bot.start(**kwargs)
            yield bot
            bot.driver.quit()
        except:
            bot.driver.quit()
            raise

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

    def upload_project(self, test_fname, project_name=None):
        """Tests that we can successfully upload `test_fname`.
        `project_name` is the expected name of the project; by
        default it is inferred from the file name.
        Returns a pair of (the name of the project, the url of the project sketch)
        """
        # A tempfile is used here since we want the name to be
        # unique; if the file has already been successfully uploaded
        # then the test might give a false-positive.
        with temp_copy(test_fname) as test_file:
            self.dropzone_upload("#dropzoneForm", test_file.name)
            if project_name is None:
                project_name = os.path.split(test_file.name)[-1].split('.')[0]

            # The upload was successful <==> we get a green "check" on its
            # Dropzone upload indicator
            self.get_element(By.CSS_SELECTOR, '#dropzoneForm .dz-success')

        # Make sure the project shows up in the Projects list
        last_project = self.get_element(By.CSS_SELECTOR,
            '#sidebar-list-main li:last-child .project_link')

        return last_project.text, last_project.get_attribute('href')

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

    def get_elements(self, *locator):
        """Like `get_element`, but returns a list of all elements matching
        the selector."""
        WebDriverWait(self.driver, ELEMENT_FIND_TIMEOUT).until(
            expected_conditions.visibility_of_all_elements_located_by(locator))
        return self.driver.find_elements(*locator)

    def get(self, selector):
        """Alias for `self.get_element(By.CSS_SELECTOR, selector)`."""
        return self.get_element(By.CSS_SELECTOR, selector)

    def get_all(self, selector):
        """Alias for `self.get_elements(By.CSS_SELECTOR, selector)`."""
        return self.get_elements(By.CSS_SELECTOR, selector)

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
        # In the BACHELOR site the id is 'operation_output', but in the live
        # site the id is 'cb_cf_operation_output'. The [id$=operation_output]
        # here selects an id that _ends_ with 'operation_output'.
        compile_result = WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            any_text_to_be_present_in_element((By.CSS_SELECTOR, "[id$=operation_output]"),
                VERIFICATION_SUCCESSFUL_MESSAGE, VERIFICATION_FAILED_MESSAGE))
        if compile_result != VERIFICATION_SUCCESSFUL_MESSAGE:
            raise VerificationError(compile_result)


    def dropzone_upload(self, selector, fname):
        """Uploads a file specified by `fname` via the Dropzone within the
        element specified by `selector`. (Dropzone refers to Dropzone.js)
        """
        # Create an artificial file input.
        self.execute_script(_CREATE_INPUT_SCRIPT)
        test_input = self.get_element(By.ID, _TEST_INPUT_ID)
        test_input.send_keys(fname)
        self.execute_script(_move_file_to_dropzone_script(selector))

    def compile_all_sketches(self, url, selector, **kwargs):
        """Compiles all sketches on the page at `url`. `selector` is a CSS selector
        that should select all relevant <a> tags containing links to sketches.
        See `compile_sketches` for the possible keyword arguments that can be specified.
        """
        self.open(url)
        sketches = self.execute_script(_GET_SKETCHES_SCRIPT.format(selector=selector))
        assert len(sketches) > 0
        self.compile_sketches(sketches, **kwargs)

    def compile_sketches(self, sketches, iframe=False, logfile=None):
        """Compiles the sketches with URLs given by the `sketches` list.
        `logfile` specifies a path to a file to which test results will be
        logged. If it is not `None`, compile errors will not cause the test
        to halt, but rather be logged to the given file. `logfile` may be a time
        format string, which will be formatted appropriately.
        `iframe` specifies whether the urls pointed to by `selector` are contained
        within an iframe.
        If the `--full` argument is provided (and hence
        `self.run_full_compile_tests` is `True`, we do not log, and limit the
        number of sketches compiled to 1.
        """
        sketch_limit = None if self.run_full_compile_tests else 1
        if logfile is None or not self.run_full_compile_tests:
            for sketch in sketches[:sketch_limit]:
                self.compile_sketch(sketch, iframe=iframe)
        else:
            log_entry = {'url': self.site_url, 'succeeded': [], 'failed': []}
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
            # Dump the test results to `logfile`.
            f = open(strftime(logfile, gmtime()), 'w')
            json.dump(log_entry, f)
            f.close()

    def execute_script(self, script, *deps):
        """Waits for all JavaScript variables in `deps` to be defined, then
        executes the given script."""
        if len(deps) > 0:
            WebDriverWait(self.driver, DOM_PROPERTY_DEFINED_TIMEOUT).until(
                dom_properties_defined(*deps))
        return self.driver.execute_script(script)


class SeleniumTestCase(CodebenderSeleniumBot):
    """Base class for all Selenium tests."""

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def _testcase_attrs(cls, webdriver, testing_url, testing_full):
        """Sets up any class attributes to be used by any SeleniumTestCase.
        Here, we just store fixtures as class attributes. This allows us to avoid
        the pytest boilerplate of getting a fixture value, and instead just
        refer to the fixture as `self.<fixture>`.
        """
        cls.driver = webdriver
        cls.site_url = testing_url
        cls.run_full_compile_tests = testing_full

    @pytest.fixture(scope="class")
    def tester_login(self):
        self.login()


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
