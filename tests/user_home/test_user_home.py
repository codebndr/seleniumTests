import os

from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TEST_DATA_BLANK_PROJECT
from codebender_testing.config import TEST_DATA_BLANK_PROJECT_ZIP
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.utils import temp_copy


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

    def _upload_test(self, test_fname, project_name=None):
        """Tests that we can successfully upload `test_fname`.
        `project_name` is the expected name of the project; by
        default it is inferred from the file name.
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

        assert last_project.text == project_name

        # Cleanup. If the above assertion failed, then we leave
        # garbage behind. This is unavoidable for now since we don't
        # have proper test fixtures. (TODO?)
        self.delete_project(project_name)

    def test_upload_project_ino(self):
        """Tests that we can upload a .ino file."""
        self._upload_test(TEST_DATA_BLANK_PROJECT)

    def test_upload_project_zip(self):
        """Tests that we can successfully upload a zipped project."""
        # TODO: how is the project name inferred from the zip file?
        # Hardcoding the contents of the zip file feels weird here.
        self._upload_test(TEST_DATA_BLANK_PROJECT_ZIP, "blank_project")

