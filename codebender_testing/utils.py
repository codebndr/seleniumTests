from contextlib import contextmanager
from time import gmtime
from time import strftime
from time import strptime
from urlparse import urlparse
import time
import random
import os
import re
import sys
import shutil
import tempfile
import simplejson
import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from codebender_testing.config import BASE_URL
from codebender_testing.config import TIMEOUT
from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.config import get_path
from codebender_testing.config import jsondump
from codebender_testing.disqus import DisqusWrapper


# Time to wait until we give up on a DOM property becoming available.
DOM_PROPERTY_DEFINED_TIMEOUT = 30

# JavaScript snippet to extract all the links to sketches on the current page.
# `selector` is a CSS selector selecting these links.
_GET_SKETCHES_SCRIPT = "return $('{selector}').map(function() {{ return this.href; }}).toArray();"

def SELECT_BOARD_SCRIPT(board):
    return """
    $('#cb_cf_boards').val('{}').trigger('change');
    """.format(board)

# JavaScript snippet to verify the code on the current page.
_VERIFY_SCRIPT = """
compilerflasher.verify();
"""

_TEST_INPUT_ID = "_cb_test_input"

# Creates an input into which we can upload files using Selenium.
_CREATE_INPUT_SCRIPT = """
var input = $('<input id="{input_id}" type="file" style="position: fixed">');
$('body').append(input);
""".format(input_id=_TEST_INPUT_ID)

# After the file is chosen via Selenium, this script moves the file object
# (in the DOM) to the Dropzone.
def _move_file_to_dropzone_script(dropzone_selector):
    return """
    $(function () {{
        var fileInput = document.getElementById('{input_id}');
        var file = fileInput.files[0];
        var dropzone = Dropzone.forElement('{selector}');
        dropzone.drop({{ dataTransfer: {{ files: [file] }} }});
      }})
    """.format(input_id=_TEST_INPUT_ID, selector=dropzone_selector)

# How long (in seconds) to wait before assuming that an example
# has failed to compile
VERIFY_TIMEOUT = 30

# Messages displayed to the user after verifying a sketch.
VERIFICATION_SUCCESSFUL_MESSAGE = "Verification Successful"
VERIFICATION_FAILED_MESSAGE = "Verification failed."

VERIFICATION_SUCCESSFUL_MESSAGE_EDITOR = 'Verification successful!'
VERIFICATION_FAILED_MESSAGE_EDITOR = 'Verification failed!'

# Max test runtime into saucelabs
# 2.5 hours (3 hours max)
SAUCELABS_TIMEOUT_SECONDS = 10800 - 1800

# Throttle between compiles
COMPILES_PER_MINUTE = 10
def throttle_compile():
    min = 60 / COMPILES_PER_MINUTE
    max = min + 1
    time.sleep(random.uniform(min, max))

BOARDS_FILE = 'boards_db.json'
BOARDS_PATH = get_path('data', BOARDS_FILE)
with open(BOARDS_PATH) as f:
    BOARDS_DB = simplejson.loads(f.read())

# Display progress
def display_progress(status):
    sys.stdout.write(status)
    sys.stdout.flush()

def read_last_log(compile_type):
    logs = os.listdir(get_path('logs'))
    logs_re = re.compile(r'.+cb_compile_tester.+')
    if compile_type == 'library':
        logs_re = re.compile(r'.+libraries_test.+')
    elif compile_type == 'fetch':
        logs_re = re.compile(r'.+libraries_fetch.+')
    elif compile_type == 'target_library':
        logs_re = re.compile(r'.+target_libraries.+')

    logs = sorted([x for x in logs if x != '.gitignore' and logs_re.match(x)])

    log_timestamp_re = re.compile(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-.+\.json')
    log = None
    timestamp = None
    if len(logs) > 0:
        log = logs[-1]
        timestamp = log_timestamp_re.match(log).group(1)

    last_log = None
    if log:
        with open(get_path('logs', log)) as f:
            last_log = simplejson.loads(f.read())

    return {
        'log': last_log,
        'timestamp': timestamp
    }


def report_creator(compile_type, log_entry, log_file):
    """Creates a report json after each compile.
    `logs`: a list in which all log files located in logs directory are added.
    `logs_to_examine`: the list of all log files located in logs directory sorted.
    `tail`: the two most recent logs in logs directory.
    `diff`: a dictionary where all differences between the two logs are stored.
    `changes`: a counter indicating the number of differences found between the two logs.
    """

    logs = os.listdir(get_path('logs'))

    logs_re = re.compile(r'.+cb_compile_tester.+')
    if compile_type == 'library':
        logs_re = re.compile(r'.+libraries_test.+')
    elif compile_type == 'fetch':
        logs_re = re.compile(r'.+libraries_fetch.+')
    elif compile_type == 'target_library':
        logs_re = re.compile(r'.+target_libraries.+')

    logs = sorted([x for x in logs if logs_re.match(x)])
    tail = logs[-2:]

    # Opens the last, or the last two log files and gathers all their contents.
    logs_to_examine = []
    for log in tail:
        try:
            with open(get_path('logs', log)) as f:
                logs_to_examine.append(simplejson.loads(f.read()))
        except:
            print 'Log:', log, 'not found'

    diff = {}
    changes = 0

    # We have only one log file, it is the first time we run the test.
    if len(logs_to_examine) == 1:
        diff = logs_to_examine[0]
        changes += 1

    # We have more than one log files, it is not the first time we run the test.
    if len(logs_to_examine) >= 2:

        old_log = logs_to_examine[0]
        new_log = logs_to_examine[1]

        #Iterate over all new_log keys (urls).
        for url in new_log.keys():

            # Check if key (url) is included in `old_log`. If not, add an entry to `diff` dictionary.
            if url not in old_log:
                diff[url] = new_log[url]
                changes += 1
                continue

            """Check if log comes from test test_libraries_fetch.py test.
            If yes, we check if the `old_log[url]`value is the same with
            `new_log[url]`value. If not, add an entry to `diff` dictionary."""
            if compile_type == 'fetch':
                if old_log[url] != new_log[url]:
                    diff[url] = new_log[url]
                    changes += 1
                continue

            """Iterate over all `new_log[url]` keys. Keys can have one of the following
            values: 'success', 'fail', 'open_fail', 'error', 'comment'."""
            for result in new_log[url].keys():

                """Check if for the specific url, result is included in
                `old_log[url]` keys. If not, check if specific url has an entry in
                `diff` dictionary and if not create one. Then add the `result` value.
                e.g. `result`: success
                     `old_log[url].keys()`: ['fail', 'success']"""

                if result not in old_log[url].keys():
                    if url not in diff:
                        diff[url] = {}
                    diff[url][result] = new_log[url][result]
                    changes += 1
                    continue

                # Check if for the specific url, the result is `comment` or `open_fail` or `error`.
                if result == 'comment' or result == 'open_fail' or result == 'error':
                    # Check if the value for the specific result is the same in both logs.
                    if old_log[url][result] != new_log[url][result]:
                        # Check if the url is on diff dictionary, if not I add it.
                        if url not in diff:
                            diff[url] = {}
                        diff[url][result] = new_log[url][result]
                        changes += 1

                # Check if for the specific url, the result is `success` or `fail`.
                elif result == 'success' or result == 'fail':
                    for board in new_log[url][result]:
                        if board not in old_log[url][result]:
                            if url not in diff:
                                diff[url] = {}
                            if result not in diff[url]:
                                diff[url][result] = []
                            diff[url][result].append(board)
                            changes += 1

    #Create report and write the results.
    filename_tokens = os.path.basename(log_file).split('.')
    filename = '.'.join(filename_tokens[0:-1])
    extension = filename_tokens[-1]
    filename = 'report_' + filename + '_' + str(changes) + '.' + extension
    path = get_path('reports', filename)
    with open(path, 'w') as f:
        f.write(jsondump(diff))


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

    def init(self, url=None, webdriver=None):
        """Create a bot with the given selenium webdriver, operating on `url`.
        We can't do this in an __init__ method, otherwise py.test complains,
        presumably because it does something special with __init__ for test
        cases.
        """
        self.driver = webdriver

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

    def login(self, credentials=None):
        """Performs a login. Note that the current URL may change to an
        unspecified location when calling this function.
        `credentials` should be a dict with keys 'username' and 'password',
        mapped to the appropriate values."""
        try:
            self.open()
            login_button = self.driver.find_element_by_id('login_btn')
            login_button.send_keys(Keys.ENTER)
            # Enter credentials and log in
            user_field = self.driver.find_element_by_id('username')
            user_field.send_keys(credentials['username'])
            pass_field = self.driver.find_element_by_id('password')
            pass_field.send_keys(credentials['password'])
            do_login = self.driver.find_element_by_id('_submit')
            do_login.send_keys(Keys.ENTER)
        except NoSuchElementException:
            # 'Log In' is not displayed, so we're already logged in.
            pass

    def logout(self):
        """Logs out of the site."""
        try:
            logout_button = self.driver.find_element_by_id("logout")
            logout_button.send_keys(Keys.ENTER)
            self.get_element(By.CSS_SELECTOR, '#login_btn')
        except NoSuchElementException:
            # 'Log out' is not displayed, so we're already logged out.
            pass

    def get_element(self, *locator):
        """Waits for an element specified by *locator (a tuple of
        (By.<something>, str)), then returns it if it is found."""
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.visibility_of_element_located(locator))
        return self.driver.find_element(*locator)

    def get_elements(self, *locator):
        """Like `get_element`, but returns a list of all elements matching
        the selector."""
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def find(self, selector):
        """Alias for self.get_element(By.CSS_SELECTOR, selector)."""
        return self.get_element(By.CSS_SELECTOR, selector)

    def find_all(self, selector):
        """Alias for self.get_elements(By.CSS_SELECTOR, selector)."""
        return self.get_elements(By.CSS_SELECTOR, selector)

    def dropzone_upload(self, selector, fname):
        """Uploads a file specified by `fname` via the Dropzone within the
        element specified by `selector`. (Dropzone refers to Dropzone.js)
        """
        # Create an artificial file input.
        self.execute_script(_CREATE_INPUT_SCRIPT, '$')
        test_input = self.get_element(By.ID, _TEST_INPUT_ID)
        test_input.send_keys(fname)
        self.execute_script(_move_file_to_dropzone_script(selector), '$', 'Dropzone')

    def upload_project(self, dropzone_selector, test_fname, sketch_name=None):
        """Tests that we can successfully upload `test_fname`.
        `project_name` is the expected name of the project; by
        default it is inferred from the file name.
        Returns a pair of (the name of the project, the url of the project sketch)
        """
        # A tempfile is used here since we want the name to be
        # unique; if the file has already been successfully uploaded
        # then the test might give a false-positive.
        with temp_copy(test_fname) as test_file:
            self.dropzone_upload(dropzone_selector, test_file.name)

            if sketch_name:
                return sketch_name
            return '.'.join(os.path.basename(test_file.name).split('.')[0:-1])

    def delete_project(self, project_name):
        """Deletes the project specified by `project_name`. Note that this will
        navigate to the user's homepage."""
        self.open('/')
        try:
            created_project = self.get_element(By.LINK_TEXT, project_name)
            delete_button_li = created_project.find_element_by_xpath('../..')
            delete_button = delete_button_li.find_element_by_css_selector('.sketch-block-controls :nth-child(3)')
            delete_button.click()
            popup_delete_button = self.get_element(By.CSS_SELECTOR, '#home-delete-sketch-modal :nth-child(4) :nth-child(2)')
            popup_delete_button.click()
            popup_delete_message = self.get_element(By.CSS_SELECTOR, '#home-delete-sketch-modal .modal-footer.delete-sketch-modal-footer .delete-sketch-modal-message.success')
            assert popup_delete_message.text == "Sketch was deleted!"
            popup_close_button = self.get_element(By.CSS_SELECTOR, '#home-delete-sketch-modal :nth-child(4) :nth-child(3)')
            popup_close_button.click()
            WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "#home-delete-sketch-modal")
                )
            )
        except:
            print "An action failed during deletion process of project:", project_name

    def resume_log (self, logfile, compile_type, sketches):
        """Resume previous log, if any. Coves 3 cases:
        Case 1: Test runs for 1st time and there is no previous log file.
        Case 2: Test runs for 2nd time and there is a previous log file which contains
        some of the urls that should be compiled and log file should be completed with
        the rest.
        Case 3: Test runs for 2nd time and there is a previous log file which contains
        all the urls that should be compiled and test should be run again for all urls.
        """
        #Creates a variable in which current date and time are stored.
        log_time = gmtime()

        #Creates an empty dictionary each time that a test runs.
        log_entry = {}

        #Creates an empty dictionary each time that a test runs.
        urls_visited = {}

        """Calls `read_last_log` function and checks if there is a previous log file
        of the same compile_type (e.g. sketch). If there is, a dictionary containing
        `timestamp` and `log` keys with their corresponding values is returned.
        Otherwise, a dictionary where `timestamp` and `log` values are `None` is returned.
        No previous log:
        {'timestamp': None, 'log': None}
        Previous log exists:
        {'timestamp': '2016-02-14_10-42-17',
         'log': {
                'https://staging.codebender.cc/sketch:30360': {'success': ['Arduino Uno']},
                'https://staging.codebender.cc/sketch:30352': {'success': ['Arduino Uno']}
                }
        }
        """
        last_log = read_last_log(compile_type)

        if compile_type != 'target_library' and last_log['log']:
            """Checks if `last_log[log]` has a value (is not `None`).
            If it has, this means that there is a log file created previously and dictionaries
            `log_entry` and `urls_visited` should be updated.
            {'timestamp': '2016-02-14_12-44-16',
             'log': {
                    'https://staging.codebender.cc/sketch:30360': {'success': ['Arduino Uno']},
                    'https://staging.codebender.cc/sketch:30352': {'success': ['Arduino Uno']}
                    }
            }
            """
            if last_log['log']:
                log_time = strptime(last_log['timestamp'], '%Y-%m-%d_%H-%M-%S')

                """ Test has stopped its execution for some reason, (e.g.to avoid saucelabs timeout)
                and `log_entry` dictionary will be filled with the entries of `last_log[log]` values.
                log_entry = {'https://staging.codebender.cc/sketch:30360': {'success': ['Arduino Uno']},
                             'https://staging.codebender.cc/sketch:30352': {'success': ['Arduino Uno']}}
                """
                log_entry = last_log['log']

                """ Test has stopped its execution for some reason,(e.g.to avoid saucelabs timeout)
                and `urls_visited` dictionary will be filled with the urls already visited when the test stopped.
                urls_visited = {'https://staging.codebender.cc/sketch:30360': True,
                                'https://staging.codebender.cc/sketch:30352': True}
                """
                for url in last_log['log']:
                    urls_visited[url] = True

        #Creates an empty dictionary each time that a test runs.
        urls_to_visit = []

        """If a test has stopped its execution for some reason,
        (e.g.to avoid saucelabs timeout) `urls_to_visit` dictionary will
        be filled with the urls that remain to be visited.
        urls_to_visit = {'https://staging.codebender.cc/sketch:30358',
                         'https://staging.codebender.cc/sketch:30355'}
        """
        for url in sketches:
            if url not in urls_visited:
                urls_to_visit.append(url)

        """If the urls_to_visit is empty, this means that the test was completed
        and should start again. `urls_to_visit` equals to all `sketches` and `log_entry`
        is an empty dictionary.
        """
        if len(urls_to_visit) == 0:
            urls_to_visit = sketches
            log_entry = {}
            log_time = gmtime()

        #If `logfile` has a value and is not `None` we create `log_file`.
        if logfile:
            log_file = strftime(logfile, log_time)

        return (urls_to_visit, log_entry, log_file, log_time)

    def create_log (self, log_file, log_entry, compile_type):
        # Dump the test results to `log_file`.
        with open(log_file, 'w') as f:
            f.write(jsondump(log_entry))

    def open_all_libraries_and_examples(self, url, logfile):
        self.open(url)
        examples = self.execute_script(_GET_SKETCHES_SCRIPT.format(selector='.accordion li a'), '$')
        assert len(examples) > 0
        libraries = self.execute_script(_GET_SKETCHES_SCRIPT.format(selector='.library_link'), '$')
        assert len(libraries) > 0
        examples_libraries = examples + libraries
        compile_type = 'fetch'
        urls_to_visit, log_entry, log_file, log_time = self.resume_log(logfile, compile_type, examples_libraries)

        libraries_re = re.compile(r'/libraries$')
        library_re = re.compile(r'/library/.+$')
        example_re = re.compile(r'/example/.+/.+$')

        print '\nVisiting:', len(urls_to_visit), 'URLs'
        tic = time.time()
        for url in urls_to_visit:
            self.open(url)
            self.get_element(By.CSS_SELECTOR, '#mycontainer')
            if library_re.match(url):
                url_name = url.split('/')[-1]
                name = self.get_element(By.CSS_SELECTOR, '#mycontainer h1 small').text
                name = re.sub('[()]', '', name).split('.')[0]
                if name != url_name:
                    print "Didn't open url: ", url

            test_status = True
            if library_re.match(url) and libraries_re.match(self.driver.current_url):
                test_status = False
            elif example_re.match(url) and 'Sorry! The example could not be fetched.' in self.driver.page_source:
                test_status = False
            log_entry[url] = test_status

            progress = '.'
            if not test_status:
                progress = 'F'

            sys.stdout.write(progress)
            sys.stdout.flush()

            with open(log_file, 'w', 0) as f:
                f.write(jsondump(log_entry))

            toc = time.time()
            if toc - tic >= SAUCELABS_TIMEOUT_SECONDS:
                print '\nStopping tests to avoid saucelabs timeout'
                print 'Test duration:', int(toc - tic), 'sec'
                return

        report_creator('fetch', log_entry, log_file)

    def compile_sketch(self, url, boards, iframe=False, project_view=False):
        """Compiles the sketch located at `url`, or an iframe within the page
        referred to by `url`.  Raises an exception if it does not compile.
        """
        self.open(url)
        # When example does not load
        if 'Sorry! The example could not be fetched.' in self.driver.page_source:
            compilation_results = []
            result = {}
            result['status'] = 'open_fail'
            compilation_results.append(result)
            return compilation_results
        # Switch into iframe if needed
        if iframe:
            self.switch_into_iframe(url)
        # Compile the target for each provided board
        compilation_results = []
        for board in boards:
            result = {
                'board': board
            }
            verification_success_message = VERIFICATION_SUCCESSFUL_MESSAGE_EDITOR
            verification_failed_message = VERIFICATION_FAILED_MESSAGE_EDITOR
            if project_view or iframe:
                verification_success_message = VERIFICATION_SUCCESSFUL_MESSAGE
                verification_failed_message = VERIFICATION_FAILED_MESSAGE
            try:
                self.execute_script(SELECT_BOARD_SCRIPT(board), '$', 'compilerflasher.pluginHandler.plugin_found')
                self.execute_script(_VERIFY_SCRIPT, 'compilerflasher')
                # The [id$=operation_output] here selects an id that _ends_ with 'operation_output'.
                compile_result = WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                    any_text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "[id$=operation_output]"),
                        verification_success_message, verification_failed_message
                    )
                )
            except WebDriverException as error:
                compile_result = "%s; %s" % (type(error).__name__, str(error))
                result['status'] = 'error'
                result['message'] = compile_result
            if compile_result == verification_success_message:
                result['status'] = 'success'
            else:
                result['status'] = 'fail'

            compilation_results.append(result)

            throttle_compile()

        self.driver.switch_to_default_content()

        return compilation_results

    def comment_compile_libraries_examples(self, sketches, library_examples_dic={}, iframe=False, project_view=False,
                                           logfile=None, compile_type='sketch', create_report=False, comment=False):

        urls_to_visit, log_entry, log_file, log_time = self.resume_log(logfile, compile_type, sketches)

        # Initialize DisqusWrapper.
        disqus_wrapper = DisqusWrapper(log_time)

        print '\nCommenting and compiling:', len(urls_to_visit), 'libraries and examples.'

        total_sketches = len(urls_to_visit)
        tic = time.time()
        library_re = re.compile(r'^.+/library/.+$')

        for url in urls_to_visit:
            if library_re.match(url):
                library = url.split('/')[-1]
                try:
                    # Comment libraries without examples
                    if len(library_examples_dic[library]) == 0:
                        if logfile is None or not self.run_full_compile_tests:
                            toc = time.time()
                            continue

                        # Update Disqus comments.
                        current_date = strftime('%Y-%m-%d', log_time)
                        if comment and compile_type in ['library', 'target_library']:
                            self.open(url)
                            self.get_element(By.CSS_SELECTOR, '#mycontainer h1')
                            examples = False
                            log_entry = disqus_wrapper.handle_library_comment(library, current_date, log_entry, examples)
                        self.create_log(log_file, log_entry, compile_type)

                        test_status = '.'
                        if not log_entry[url]['comment']:
                            test_status = 'F'
                        display_progress(test_status)
                except Exception as error:
                    print error

                toc = time.time()
                if (toc - tic) >= SAUCELABS_TIMEOUT_SECONDS:
                    print '\nStopping tests to avoid saucelabs timeout'
                    print 'Test duration:', int(toc - tic), 'sec'
                    return
            else:
                sketch = url
                # Read the boards map in case current sketch/example requires a special board configuration.
                boards = BOARDS_DB['default_boards']
                url_fragments = urlparse(sketch)
                if url_fragments.path in BOARDS_DB['special_boards']:
                    boards = BOARDS_DB['special_boards'][url_fragments.path]

                if len(boards) > 0:
                    # Run Verify.
                    results = self.compile_sketch(sketch, boards, iframe=iframe, project_view=project_view)
                else:
                    results = [
                        {
                            'status': 'unsupported'
                        }
                    ]

                """If test is not running in full mode (-F option) or logfile is None
                no logs are produced inside /logs directory and we continue with sketches
                compilation.
                """
                if logfile is None or not self.run_full_compile_tests:
                    toc = time.time()
                    continue

                # Register current URL into log.
                if sketch not in log_entry:
                    log_entry[sketch] = {}

                test_status = '.'

                # Log the compilation results.
                openFailFlag = False
                for result in results:
                    if result['status'] in ['success', 'fail', 'error'] and result['status'] not in log_entry[sketch]:
                        log_entry[sketch][result['status']] = []
                    if result['status'] == 'success':
                        log_entry[sketch]['success'].append(result['board'])
                    elif result['status'] == 'fail':
                        log_entry[sketch]['fail'].append(result['board'])
                        test_status = 'F'
                    elif result['status'] == 'open_fail':
                        log_entry[sketch]['open_fail'] = True
                        openFailFlag = True
                        test_status = 'O'
                    elif result['status'] == 'error':
                        log_entry[sketch]['error'].append({
                            'board': result['board'],
                            'error': result['message']
                        })
                        test_status = 'E'
                    elif result['status'] == 'unsupported':
                        log_entry[sketch]['unsupported'] = True
                        test_status = 'U'

                # Update Disqus comments.
                current_date = strftime('%Y-%m-%d', log_time)

                if comment and compile_type in ['library', 'target_library']:
                    log_entry = disqus_wrapper.update_comment(sketch, results, current_date, log_entry, openFailFlag, total_sketches)

                self.create_log(log_file, log_entry, compile_type)

                display_progress(test_status)

                toc = time.time()
                if (toc - tic) >= SAUCELABS_TIMEOUT_SECONDS:
                    print '\nStopping tests to avoid saucelabs timeout'
                    print 'Test duration:', int(toc - tic), 'sec'
                    return

        # Generate a report if requested.
        if compile_type != 'target_library' and create_report and self.run_full_compile_tests:
            report_creator(compile_type, log_entry, log_file)
        print '\nTest duration:', int(toc - tic), 'sec'

    def compile_all_sketches(self, url, selector, **kwargs):
        """Compiles all sketches on the page at `url`. `selector` is a CSS selector
        that should select all relevant <a> tags containing links to sketches.
        See `compile_sketches` for the possible keyword arguments that can be specified.
        """
        self.open(url)
        sketches = self.execute_script(_GET_SKETCHES_SCRIPT.format(selector=selector), '$')
        assert len(sketches) > 0
        self.compile_sketches(sketches, **kwargs)

    def compile_sketches(self, sketches, iframe=False, project_view=False, logfile=None, compile_type='sketch', create_report=False, comment=False):
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

        urls_to_visit, log_entry, log_file, log_time = self.resume_log(logfile, compile_type, sketches)

        # Initialize DisqusWrapper.
        disqus_wrapper = DisqusWrapper(log_time)

        print '\nCompiling:', len(urls_to_visit), 'sketches'
        total_sketches = len(urls_to_visit)
        tic = time.time()

        for sketch in urls_to_visit:
            # Read the boards map in case current sketch/example requires a special board configuration.
            boards = BOARDS_DB['default_boards']
            url_fragments = urlparse(sketch)
            if url_fragments.path in BOARDS_DB['special_boards']:
                boards = BOARDS_DB['special_boards'][url_fragments.path]

            if len(boards) > 0:
                # Run Verify.
                results = self.compile_sketch(sketch, boards, iframe=iframe, project_view=project_view)
            else:
                results = [
                    {
                        'status': 'unsupported'
                    }
                ]

            """If test is not running in full mode (-F option) or logfile is None
            no logs are produced inside /logs directory and we continue with sketches
            compilation.
            """
            if logfile is None or not self.run_full_compile_tests:
                toc = time.time()
                continue

            # Register current URL into log.
            if sketch not in log_entry:
                log_entry[sketch] = {}

            test_status = '.'

            # Log the compilation results.
            openFailFlag = False
            for result in results:
                if result['status'] in ['success', 'fail', 'error'] and result['status'] not in log_entry[sketch]:
                    log_entry[sketch][result['status']] = []
                if result['status'] == 'success':
                    log_entry[sketch]['success'].append(result['board'])
                elif result['status'] == 'fail':
                    log_entry[sketch]['fail'].append(result['board'])
                    test_status = 'F'
                elif result['status'] == 'open_fail':
                    log_entry[sketch]['open_fail'] = True
                    openFailFlag = True
                    test_status = 'O'
                elif result['status'] == 'error':
                    log_entry[sketch]['error'].append({
                        'board': result['board'],
                        'error': result['message']
                    })
                    test_status = 'E'
                elif result['status'] == 'unsupported':
                    log_entry[sketch]['unsupported'] = True
                    test_status = 'U'

            # Update Disqus comments.
            current_date = strftime('%Y-%m-%d', log_time)
            if comment and compile_type in ['library', 'target_library']:
                log_entry = disqus_wrapper.update_comment(sketch, results, current_date, log_entry, openFailFlag, total_sketches)

            self.create_log(log_file, log_entry, compile_type)

            display_progress(test_status)

            toc = time.time()
            if toc - tic >= SAUCELABS_TIMEOUT_SECONDS:
                print '\nStopping tests to avoid saucelabs timeout'
                print 'Test duration:', int(toc - tic), 'sec'
                return

        # Generate a report if requested.
        if compile_type != 'target_library' and create_report and self.run_full_compile_tests:
            report_creator(compile_type, log_entry, log_file)
        print '\nTest duration:', int(toc - tic), 'sec'

    def execute_script(self, script, *deps):
        """Waits for all JavaScript variables in `deps` to be defined, then
        executes the given script."""
        if len(deps) > 0:
            WebDriverWait(self.driver, DOM_PROPERTY_DEFINED_TIMEOUT).until(
                dom_properties_defined(*deps)
            )
        return self.driver.execute_script(script)

    def create_sketch(self, privacy, name, description):
        """Creates a sketch with a given name"""
        createSketchBtn = self.get_element(By.ID, 'create_sketch_btn')
        createSketchBtn.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                expected_conditions.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#create-sketch-modal")
                )
            )

        self.change_privacy(privacy)

        self.change_name(name)

        self.change_short_description(description)

        createBtn = self.get_element(By.ID, 'create-sketch-modal-action-button')
        createBtn.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "#editor-loading-screen")
                )
            )
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "#editor_heading_project_name")
            )
        )

    def change_privacy(self, privacy):
        privateRadioButton = self.get_element(By.CSS_SELECTOR,'#create-sketch-modal-type-controls [value="public"]')
        if privacy == 'private':
            privateRadioButton = self.get_element(By.CSS_SELECTOR,'#create-sketch-modal-type-controls [value="private"]')
        privateRadioButton.click()

    def change_name(self, name):
        print name
        nameField = self.get_element(By.CSS_SELECTOR,'#create-sketch-modal .modal-body [id="create-sketch-name"')
        print nameField
        nameField.clear()
        nameField.send_keys(name)
        nameField.send_keys(Keys.ENTER)

    def change_name_editor(self, name):
        sketchHeading = self.get_element(By.ID, 'editor_heading_project_name')
        sketchHeading.click()
        renameInput = '#editor_heading_project_name input'
        headingInput = self.get_element(By.CSS_SELECTOR, renameInput)
        headingInput.clear()
        headingInput.send_keys(name)
        headingInput.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, "#editor_heading_project_working")
            )
        )
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), 'Name successfully changed!'
            )
        )

    def change_short_description(self, description):
        nameField = self.get_element(By.CSS_SELECTOR,'#create-sketch-modal-sort-description')
        nameField.clear()
        nameField.send_keys(description)
        nameField.send_keys(Keys.ENTER)

    def change_short_description_editor(self, description):
        editDescription = self.get_element(By.CSS_SELECTOR,'.short-description-edit')
        editDescription.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.visibility_of(
                self.get_element(By.CSS_SELECTOR, '#editor-description-modal')
            )
        )
        shortDescriptionField = self.get_element(By.CSS_SELECTOR,'#editor-description-modal .modal-body [id="short-description-modal-input"]')
        shortDescriptionField.clear()
        shortDescriptionField.send_keys(description)
        shortDescriptionField.send_keys(Keys.ENTER)
        saveButton = self.get_element(By.CSS_SELECTOR,'#editor-description-modal .modal-footer .btn-success')
        saveButton.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR,'#editor-description-modal .modal-footer #editor-description-modal-message'), 'Sketch description saved.'
            )
        )
        closeButton = self.get_element(By.CSS_SELECTOR,'#editor-description-modal .modal-footer .btn-danger')
        closeButton.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, '#editor-description-modal')
            )
        )

    def check_iframe(self):
        """Returns the contents of an iframe [project_name, user_name, sketch_contents]"""
        self.driver.switch_to_frame(self.driver.find_element_by_tag_name('iframe'))
        project_name = self.driver.find_element_by_class_name('projectName').text
        user_name = self.driver.find_element_by_class_name('userName').text
        sketch_contents = self.execute_script('return editor.aceEditor.getValue();', 'editor')
        self.driver.switch_to_default_content()
        return [project_name, user_name, sketch_contents]

    def switch_into_iframe(self, url):
        if 'embed' not in url:
            url = url.replace('https://codebender.cc/', 'https://codebender.cc/embed/')
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.visibility_of(
                self.get_element(By.CSS_SELECTOR, 'iframe[src="' + url + '"]')
            )
        )
        script = """
        var iframes = document.body.getElementsByTagName('iframe');
        var iframe_index = 0;
        for (var i=0; i<iframes.length; i++) {{
            var iframeSrc = iframes[i].getAttribute('src');
            if (iframeSrc && iframeSrc.indexOf('{url}') > -1) {{
                iframe_index = i;
            }}
        }}
        return iframe_index;
        """.format(url=url)
        index = self.execute_script(script)
        iframe = self.driver.find_elements_by_tag_name('iframe')[index]
        self.driver.switch_to_frame(iframe)


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
    def tester_login(self, testing_credentials):
        """A fixture to perform a login with the credentials provided by the
        `testing_credentials` fixture.
        """
        self.login(credentials=testing_credentials)

    @pytest.fixture(scope="class")
    def tester_logout(self):
        """A fixture to guarantee that we are logged out before running a test."""
        self.logout()

class CodebenderEmbeddedTestCase(SeleniumTestCase):
    """base class for testing embedded views"""

    @pytest.fixture(scope="class")
    def test_embedded_sketch(self, selector):
        self.switch_into_iframe(selector)

        project_name = self.driver.find_element_by_class_name('projectName').text
        assert len(project_name) > 0

        user_name = self.driver.find_element_by_class_name('userName').text
        assert len(user_name) > 0

        edit_button = self.driver.find_element_by_id('edit-button').text
        assert edit_button == 'Edit'

        clone_link = self.driver.find_element_by_class_name('clone-link').text
        assert clone_link == 'Clone & Edit'

        download_link = self.driver.find_element_by_class_name('download-link').text
        assert download_link == 'Download'

        editor_contents = self.execute_script('return editor.aceEditor.getValue();', 'editor')
        assert len(editor_contents) > 0

        assert self.check_element_exists('#cb_cf_flash_btn') == True
        assert self.check_element_exists('#cb_cf_boards') == True
        assert self.check_element_exists('#cb_cf_ports') == True

        boards_list = self.driver.find_element_by_id('cb_cf_boards').text
        assert len(boards_list) > 0

        self.driver.switch_to_default_content()

    @pytest.fixture(scope="class")
    def test_serial_monitor(self, selector):
        self.switch_into_iframe(selector)

        title = self.driver.find_element_by_css_selector('.well > h4').text.strip()
        assert title == 'Serial Monitor:'

        ports_label = self.driver.find_element_by_css_selector('.well > span').text.strip()
        assert ports_label == 'Port:'

        assert self.check_element_exists('#cb_cf_ports') == True
        assert self.check_element_exists('#cb_cf_baud_rates') == True
        assert self.check_element_exists('#cb_cf_serial_monitor_connect') == True

    def check_element_exists(self, css_path):
        try:
            self.driver.find_element_by_css_selector(css_path)
            return True
        except NoSuchElementException:
            return False

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
