import os

from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TEST_DATA_INO
from codebender_testing.config import TEST_DATA_ZIP
from codebender_testing.config import SOURCE_BACHELOR
from codebender_testing.config import SOURCE_CODEBENDER_CC
from codebender_testing.utils import SeleniumTestCase


# Name to be used for the new project that is created.
NEW_PROJECT_NAME = 'selenium_TestUserHome'

class TestUserHome(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        pass

    @pytest.mark.requires_source(SOURCE_BACHELOR)
    def test_create_project_blank_name(self):
        """Test that we get an error when creating a project with no name."""
        create_button = self.get_element(By.CSS_SELECTOR, '.form-search button')
        create_button.click()
        error_heading = self.get_element(By.CSS_SELECTOR, '.alert h4')
        assert error_heading.text.startswith('Error')

    @pytest.mark.requires_source(SOURCE_BACHELOR)
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

    @pytest.mark.requires_source(SOURCE_BACHELOR)
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

    def _upload_test(self, dropzone_selector, test_fname, sketch_name=None):
        """Tests that we can successfully upload `test_fname`.
        `project_name` is the expected name of the project; by
        default it is inferred from the file name.
        We delete the project if it is successfully uploaded.
        """
        try:
            upload_name = self.upload_project(dropzone_selector, test_fname, sketch_name)
            assert upload_name in self.driver.page_source
        finally:
            self.delete_project(upload_name)

    @pytest.mark.requires_source(SOURCE_CODEBENDER_CC)
    def test_upload_project_ino(self):
        """Tests that we can upload a .ino file."""
        self._upload_test('#uploadInoModal form', TEST_DATA_INO)

    @pytest.mark.requires_source(SOURCE_CODEBENDER_CC)
    def test_upload_project_zip(self):
        """Tests that we can successfully upload a zipped project."""
        # TODO: how is the project name inferred from the zip file?
        # Hardcoding the contents of the zip file feels weird here.
        self._upload_test('#uploadFolderZip form', TEST_DATA_ZIP, sketch_name='upload_zip')
