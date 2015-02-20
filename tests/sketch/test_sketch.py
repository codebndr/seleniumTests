import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
import pytest

from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.utils import SeleniumTestCase


# How long to wait before we give up on trying to assess the result of commands
VERIFY_TIMEOUT = 10
FLASH_TIMEOUT = 2

# Board to test for the dropdown selector.
TEST_BOARD = "Arduino Fio"


class TestSketch(SeleniumTestCase):
    """Tests various functions of the /sketch view."""

    @pytest.fixture(scope="class", autouse=True)
    def open_test_project(self, tester_login):
        """Makes sure we are logged in and have a project open before
        performing any of these tests."""
        self.open_project()
        # I get a StaleElementReferenceException without
        # this wait. TODO: figure out how to get around this.
        time.sleep(3)
 
    def test_verify_code(self):
        """Ensures that we can compile code and see the success message."""
        compile_button = self.driver.find_element_by_id("compile")
        compile_button.click()

        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), "Verification Successful!")
        )

    def test_boards_dropdown(self):
        """Tests that the boards dropdown is present, and that we can change
        the board successfully."""
        boards_dropdown = Select(self.get_element(By.ID, "boards"))

        # Click something other than the first option
        boards_dropdown.select_by_visible_text(TEST_BOARD)

        assert boards_dropdown.first_selected_option.text == TEST_BOARD

    def test_ports_dropdown(self):
        """Tests that the ports dropdown exists."""
        self.get_element(By.ID, "ports")

    def test_run_with_no_port(self):
        """Makes sure that there is an error when we attempt to run with no
        port selected."""
        flash_button = self.get_element(By.ID, "uploadusb")
        flash_button.click()
        WebDriverWait(self.driver, FLASH_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), "Please select a valid port or enable the plugin!!"))

    def test_speeds_dropdown(self):
        """Tests that the speeds dropdown exists."""
        self.get_element(By.ID, "baudrates")

    def test_clone_project(self):
        """Tests that clicking the 'Clone Project' link brings us to a new
        sketch with the title 'test_project clone'."""
        clone_link = self.get_element(By.LINK_TEXT, 'Clone Project')
        clone_link.click()
        project_name = self.get_element(By.ID, 'editor_heading_project_name')
        assert project_name.text.startswith("%s copy" % TEST_PROJECT_NAME)

    def test_add_projectfile(self):
        """ Tests that new file can be added to project using create-new-file field """
        add_button = self.get_element(By.CLASS_NAME, 'icon-plus')
        add_button.click()
        create_field = self.get_element(By.ID, 'createfield')
        create_field.send_keys('test_file.txt')
        create_button = self.get_element(By.CLASS_NAME, 'btn')
        create_button.click()
        assert "test_file.txt" in self.driver.page_source
