from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
import pytest

from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.utils import SELECT_BOARD_SCRIPT
from codebender_testing.utils import throttle_compile


# How long to wait before we give up on trying to assess the result of commands
VERIFY_TIMEOUT = 30
FLASH_TIMEOUT = 30

# Board to test for the dropdown selector.
TEST_BOARD = "Arduino Fio"


class TestSketch(SeleniumTestCase):
    """Tests various functions of the /sketch view."""

    @pytest.fixture(scope="class", autouse=True)
    def create_test_project(self, tester_login):
        """Makes sure we are logged in and have a project open before
        performing any of these tests."""
        self.create_sketch(TEST_PROJECT_NAME)

    def test_verify_code(self):
        """Ensures that we can compile code and see the success message."""
        boards = ['Arduino Uno', 'Arduino Leonardo', 'Arduino Mega 2560 or Mega ADK']
        for board in boards:
            self.execute_script(SELECT_BOARD_SCRIPT(board))
            compile_button = self.get_element(By.ID, "cb_cf_verify_btn")
            compile_button.click()

            WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                expected_conditions.invisibility_of_element_located(
                    (By.ID, "progress"))
            )

            operation_output = self.driver.find_element_by_id('operation_output')
            assert operation_output.text.strip() == 'Verification successful!'
            throttle_compile()

    def test_boards_dropdown(self):
        """Tests that the boards dropdown is present, and that we can change
        the board successfully."""
        boards_dropdown = Select(self.get_element(By.ID, "cb_cf_boards"))

        # Click something other than the first option
        boards_dropdown.select_by_visible_text(TEST_BOARD)

        assert boards_dropdown.first_selected_option.text == TEST_BOARD

    @pytest.mark.requires_extension
    def test_ports_dropdown(self):
        """Tests that the ports dropdown exists."""
        ports = self.get_element(By.ID, "cb_cf_ports")
        assert ports.text == 'No ports detected'

    @pytest.mark.requires_extension
    def test_run_with_no_port(self):
        """Makes sure that there is an error when we attempt to run with no
        port selected."""
        flash_button = self.get_element(By.ID, "cb_cf_flash_btn")
        flash_button.click()
        WebDriverWait(self.driver, FLASH_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), "Please select a valid port!"
            )
        )

    @pytest.mark.requires_extension
    def test_speeds_dropdown(self):
        """Tests that the speeds dropdown exists."""
        self.get_element(By.ID, "cb_cf_baud_rates")

    @pytest.mark.requires_extension
    def test_serial_monitor_disables_fields(self):
        """Tests that opening the serial monitor disables the port and baudrate
        fields."""
        open_serial_monitor_button = self.get_element(By.ID, 'cb_cf_serial_monitor_connect')
        open_serial_monitor_button.click()

        WebDriverWait(self.driver, FLASH_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), 'Please select a valid port!'
            )
        )

    def test_clone_project(self):
        """Tests that clicking the 'Clone Project' link brings us to a new
        sketch with the title 'test_project clone'."""
        clone_link = self.get_element(By.ID, 'clone_btn')
        clone_link.click()
        project_name = self.get_element(By.ID, 'editor_heading_project_name')
        # Here, I use `startswith` in case the user has a bunch of
        # projects like "test_project copy copy copy" ...
        assert project_name.text.startswith("%s copy" % TEST_PROJECT_NAME)

        # Cleanup: delete the project we just created.
        self.delete_project("%s copy" % TEST_PROJECT_NAME)

    def test_add_projectfile_direct(self):
        """ Tests that new file can be added to project using create-new-file
        field """
        self.open_project()

        add_button = self.get_element(By.CLASS_NAME, 'add-file-button')
        add_button.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.visibility_of(
                self.get_element(By.ID, "creationModal")
            )
        )
        create_field = self.get_element(By.ID, 'createfield')
        create_field.send_keys('test_file.txt')
        create_button = self.get_element(By.ID, 'createbutton')
        create_button.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, "creationModal")
            )
        )
        assert 'test_file.txt' in self.driver.page_source

    def test_delete_file(self):
        """Tests file delete modal """
        delete_file_button = self.get_element(By.CLASS_NAME, 'delete-file-button')
        delete_file_button.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.visibility_of(
                self.get_element(By.ID, "filedeleteModal")
            )
        )
        assert self.get_element(By.ID, 'filedeleteModal').is_displayed()

    def test_verify_deletion(self):
        """ Verifies that file has been deleted """
        confirm_delete_button = self.get_element(By.ID, 'filedeleteButton')
        confirm_delete_button.click()
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.invisibility_of_element_located(
                (By.ID, "filedeleteModal")
            )
        )
        operation_output = self.get_element(By.ID, 'operation_output')
        assert operation_output.text.strip() == 'File successfully deleted.'
        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, '#files_list a[data-name="test_file.txt"]')
            )
        )

    def test_remove_sketch(self):
        self.delete_project(TEST_PROJECT_NAME)
