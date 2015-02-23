from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TEST_DATA_BLANK_PROJECT
from codebender_testing.utils import SeleniumTestCase


# Name to be used for the new project that is created.
NEW_PROJECT_NAME = 'selenium_TestUserHome'

class TestUserHome(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        pass

    def test_create_project_blank_name(self):
        """Test that we get an error when creating a project with no name."""
        create_button = self.get_element(By.CSS_SELECTOR, '.form-search button')
        create_button.click()
        error_heading = self.get_element(By.CSS_SELECTOR, '.alert h4')
        assert error_heading.text.startswith('Error')

    def test_create_project_invalid_name(self):
        """Test that we get an error when creating a project with an
        invalid name (e.g., a name containing a backslash).
        """
        project_name_input = self.get_element(By.CSS_SELECTOR,
                                              '.form-search input[type=text]')
        project_name_input.clear()
        project_name_input.send_keys('foo\\bar')
        create_button = self.get_element(By.CSS_SELECTOR, '.form-search button')
        create_button.click()

        error_heading = self.get_element(By.CSS_SELECTOR, '.alert h4')
        assert error_heading.text.startswith('Error')

    def test_create_project_valid_name(self):
        """Test that we can successfully create a project with a valid name."""
        project_name_input = self.get_element(By.CSS_SELECTOR,
                                              '.form-search input[type=text]')
        project_name_input.clear()
        project_name_input.send_keys(NEW_PROJECT_NAME)
        create_button = self.get_element(By.CSS_SELECTOR, '.form-search button')
        create_button.click()

        project_heading = self.get_element(By.ID, 'editor_heading_project_name')
        assert project_heading.text == NEW_PROJECT_NAME

        # Cleanup: delete the project we just created.
        self.delete_project(NEW_PROJECT_NAME)

