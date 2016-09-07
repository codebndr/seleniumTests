import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.config import TIMEOUT
import time

TEST_SKETCH = 'test_collaboration'
TEST_FILE = 'test.h'
TEST_EMPTY_FILE = 'empty.h'
TEST_RENAME_FILE = 'rename.h'
TEST_RENAMED_FILE = 'renamed.h'
TEST_INPUT = '// test input'

class TestCollaboration(SeleniumTestCase):
    ''' Opens a new tab in the browser '''
    def open_tab(self, url):
        self.execute_script('window.open("{}")'.format(url))

    ''' Closes current tab in the browser '''
    def close_tab(self):
        self.execute_script('window.close()')

    ''' Switches between tabs in the browser '''
    def switch_window(self, index):
        window = self.driver.window_handles[index]
        self.driver.switch_to.window(window)

    @pytest.fixture(scope="class", autouse=True)
    def create_test_project(self, tester_login):
        """Makes sure we are logged in and have a project open before
        performing any of these tests."""
        self.create_sketch('public' , TEST_SKETCH, '')

    def test_open_tab(self):
        self.sketch_url = self.execute_script('return location.href')
        self.open_tab(self.sketch_url)
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, "#editor-loading-screen")
            )
        )
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "#editor_heading_project_name")
            )
        )

    def test_create_file(self):
        self.switch_window(0)
        self.create_file(TEST_FILE)

    def test_check_created_file(self):
        self.switch_window(1)
        test_file = self.get_element(By.CSS_SELECTOR, '#files_list .filelist[data-name="{}"]'.format(TEST_FILE))
        filename = test_file.text.strip()
        assert filename == TEST_FILE
        test_file.click()
        self.execute_script('editor.aceEditor.setValue("{}");'.format(TEST_INPUT), 'editor')

    def test_check_contents_change(self):
        self.switch_window(0)
        while self.execute_script('return editor.aceEditor.getValue();') != TEST_INPUT:
            time.sleep(1) # Wait for editor to sync
        test_input = self.execute_script('return editor.aceEditor.getValue();')
        assert TEST_INPUT == test_input

    def test_create_and_delete_file(self):
        self.switch_window(0)
        self.create_file(TEST_EMPTY_FILE)
        self.switch_window(1)
        test_file = self.get_element(By.CSS_SELECTOR, '#files_list .filelist[data-name="{}"]'.format(TEST_EMPTY_FILE))
        filename = test_file.text.strip()
        assert filename == TEST_EMPTY_FILE
        test_file.click()
        self.execute_script('editor.aceEditor.setValue("{}");'.format(TEST_INPUT), 'editor')
        self.remove_file(filename)
        self.switch_window(0)
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.alert_is_present()
        )
        Alert(self.driver).dismiss()

    def test_check_deleted_file(self):
        self.switch_window(0)
        deleted_file = self.driver.find_elements_by_css_selector('#files_list .filelist[data-name="{}"]'.format(TEST_EMPTY_FILE))
        assert len(deleted_file) == 0
        self.create_file(TEST_EMPTY_FILE)
        empty_contents = self.execute_script('return editor.aceEditor.getValue();', 'editor')
        assert empty_contents == ''

    def test_rename_file(self):
        self.switch_window(1)
        self.create_file(TEST_RENAME_FILE)
        self.execute_script('editor.aceEditor.setValue("int a = 1;");', 'editor')
        self.execute_script('editor.aceEditor.session.selection.moveCursorToPosition({row: 0, column: 3}); editor.aceEditor.session.selection.clearSelection();', 'editor')
        self.switch_window(0)
        self.get_element(By.CSS_SELECTOR, '#files_list .filelist[data-name="{}"]'.format(TEST_RENAME_FILE)).click()
        self.rename_file(TEST_RENAME_FILE, TEST_RENAMED_FILE)
        self.switch_window(1)
        self.get_element(By.CSS_SELECTOR, '#files_list .filelist[data-name="{}"]'.format(TEST_RENAMED_FILE))

    def test_remove_sketch(self):
        self.switch_window(1)
        self.remove_sketch_editor()
        self.switch_window(0)
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.alert_is_present()
        )
        Alert(self.driver).dismiss()
        self.logout()
