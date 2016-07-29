from codebender_testing.utils import SeleniumTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from codebender_testing import config
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from codebender_testing.config import TIMEOUT
from selenium.webdriver.support.ui import WebDriverWait
import pytest

class TestSketchesCounters(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        pass

    def test_create_sketch_modal(self):
        # Create a public project.
        createSketchBtn = self.get_element(By.ID, 'create_sketch_btn')
        createSketchBtn.click()
        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, "#create-sketch-modal")
            )
        )
        createBtn = self.get_element(
            By.ID, 'create-sketch-modal-action-button')

        createdProject = self.get_element(
            By.ID, 'create-sketch-name').get_attribute('value')

        # Check that when the create sketch modal opens,
        # the sketch name input has focus.
        assert self.get_element(By.ID, 'create-sketch-name') == \
            self.driver.switch_to.active_element

        # Check that sketch name is auto-generated as:
        # Untitled Sketch CURRENT_DATE.
        current_date_text= "Untitled Sketch " + time.strftime("%Y-%m-%d")
        assert self.get_element(By.ID,
            "create-sketch-name").get_attribute("value") == current_date_text

        # Check that when the input has focus and you press Enter,
        # the create sketch action is executed.
        self.get_element(By.ID, 'create-sketch-name').send_keys(Keys.ENTER)

        self.get_element(By.CSS_SELECTOR, '#create-sketch-modal-action-button .fa-spinner')

        # Check that during the sketch creation,
        # the sketch privacy radio buttons are disabled.
        publicRadioButton = self.get_element(By.CSS_SELECTOR,
            '#create-sketch-modal-type-controls [value="public"]')
        privateRadioButton = self.get_element(By.CSS_SELECTOR,
            '#create-sketch-modal-type-controls [value="private"]')
        assert publicRadioButton.get_attribute('disabled')
        assert privateRadioButton.get_attribute('disabled')

        WebDriverWait(self.driver, TIMEOUT['LOCATE_ELEMENT']).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "#editor_heading_project_name")
            )
        )

        # Delete the created project.
        self.open("/")
        self.delete_project(createdProject)
