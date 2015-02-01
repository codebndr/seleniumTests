from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from codebender_testing.config import VERIFY_TIMEOUT
from codebender_testing.utils import logged_in
from codebender_testing.utils import SeleniumTestCase


class TestSketch(SeleniumTestCase):

    @logged_in
    def test_verify_code(self):
        test_project_link = self.driver.find_element_by_link_text('test_project')
        test_project_link.send_keys(Keys.ENTER)

        compile_button = self.driver.find_element_by_id("compile")
        compile_button.click()

        try:
            WebDriverWait(self.driver, VERIFY_TIMEOUT).until(
                expected_conditions.text_to_be_present_in_element(
                    (By.ID, "operation_output"), "Verification Successful!")
            )
        except:
            raise
            # assert False, "Test timed out"

        assert output.text == "Verification Successful!"

