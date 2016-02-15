from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TEST_DATA_INO
from codebender_testing.config import TEST_DATA_ZIP
from codebender_testing.utils import SeleniumTestCase


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
        try:
            upload_name = self.upload_project(dropzone_selector, test_fname, sketch_name)
            selector = '#project_list li[data-name="'+ str(upload_name.lower()) +'"]'
            project_uploaded = self.get_element(By.CSS_SELECTOR, selector).text.split('\n')[0]
            assert upload_name == project_uploaded
        finally:
            self.delete_project(upload_name)

    def test_upload_project_ino(self):
        """Tests that we can upload a .ino file."""
        self._upload_test('#uploadInoModal form', TEST_DATA_INO)

    def test_upload_project_zip(self):
        """Tests that we can successfully upload a zipped project."""
        # TODO: how is the project name inferred from the zip file?
        # Hardcoding the contents of the zip file feels weird here.
        self._upload_test('#uploadFolderZip form', TEST_DATA_ZIP, sketch_name='upload_zip')
