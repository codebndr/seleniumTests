import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from codebender_testing.utils import logged_in
from codebender_testing.utils import SeleniumTestCase


# How long to wait before we give up on the 'verify' command (in seconds)
VERIFY_TIMEOUT = 10

# How long to wait before we give up on finding an element on the page.
ELEMENT_FIND_TIMEOUT = 5


class TestSketch(SeleniumTestCase):

    @logged_in
    def test_verify_code(self):
        self.open_project()

        # I get a StaleElementReferenceException without
        # this wait. TODO: figure out how to get around this.
        time.sleep(3)

        compile_button = self.driver.find_element_by_id("compile")
        compile_button.click()

        WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "operation_output"), "Verification Successful!")
        )

    @logged_in
    def test_boards_dropdown(self):
        self.open_project()

        WebDriverWait(self.driver, ELEMENT_FIND_TIMEOUT).until(
            expected_conditions.presence_of_element_located(
            (By.ID, "boards"))
        )

        boards_dropdown = self.driver.find_element_by_id("boards")
        options = boards_dropdown.find_elements_by_tag_name("option")

        # Click something other than the first option
        test_option = options[3]
        test_option.click()

