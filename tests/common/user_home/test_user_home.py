from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TEST_DATA_INO
from codebender_testing.config import TEST_DATA_ZIP
from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Name to be used for the new project that is created.
NEW_PROJECT_NAME = 'selenium_TestUserHome'

class TestUserHome(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        pass

    def _upload_test(self, dropzone_selector, test_fname, sketch_name=None):
        """Tests that we can successfully upload `test_fname`.
        `project_name` is the expected name of the project; by
        default it is inferred from the file name.
        We delete the project if it is successfully uploaded.
        """
        # Upload the file.
        upload_name = self.upload_project(dropzone_selector, test_fname, sketch_name)
        # Wait for the success mark to appear before closing the modal.
        WebDriverWait(self.driver, 30).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".dz-success-mark")
            )
        )
        close_btn = self.get_element(By.CSS_SELECTOR, "#home-upload-sketch-modal .btn-danger")
        close_btn.click()
        # Check that the uploaded file appears on the homepage.
        selector = '#project_list li[data-name="'+ upload_name +'"]'
        project_uploaded = self.get_element(By.CSS_SELECTOR, selector).text.split('\n')[0]
        assert upload_name == project_uploaded
        self.delete_project(upload_name)

    def test_upload_project_ino(self):
        """Tests that we can upload a .ino file."""
        upload_button = self.get_element(By.CSS_SELECTOR, '#sketch-upload-button')
        upload_button.click()
        sketch_upload_ino = self.get_element(By.CSS_SELECTOR, '#upload-sketch-ino')
        sketch_upload_ino.click()
        self._upload_test('#dropzoneForm', TEST_DATA_INO)

    def test_upload_project_zip(self):
        """Tests that we can successfully upload a zipped project."""
        # TODO: how is the project name inferred from the zip file?
        # Hardcoding the contents of the zip file feels weird here.
        upload_button = self.get_element(By.CSS_SELECTOR, '#sketch-upload-button')
        upload_button.click()
        sketch_upload_zip = self.get_element(By.CSS_SELECTOR, '#upload-sketch-zip')
        sketch_upload_zip.click()
        self._upload_test('#dropzoneForm', TEST_DATA_ZIP, sketch_name='upload_zip')
