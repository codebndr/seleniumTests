from codebender_testing.config import COMPILE_TESTER_DIR
from codebender_testing.config import COMPILE_TESTER_LOGFILE
from codebender_testing.config import COMPILE_TESTER_LOGFILE_STAGING
from codebender_testing.config import COMPILE_TESTER_URL
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.config import STAGING_SITE_URL
from codebender_testing.config import COMPILE_TESTER_STAGING_URL
from selenium.webdriver.common.by import By
from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import os
import pytest
import time

class TestCompileTester(SeleniumTestCase):

    # Here, we require the LIVE_SITE_URL since the compiler tester user
    # does not exist anywhere else.
    @pytest.mark.requires_url(LIVE_SITE_URL)
    def test_compile_all_user_projects(self):
        """Tests that all user's sketches compile successfully."""
        self.compile_all_sketches(COMPILE_TESTER_URL, '#user_projects tbody a',
            compile_type='sketch',
            iframe=True, project_view=True,
            create_report=True, logfile=COMPILE_TESTER_LOGFILE)

    # Here we upload, compile and delete all sketches included in
    # test_data/cb_compile_tester folder using demo_user on staging site.
    @pytest.mark.requires_url(STAGING_SITE_URL)
    def test_compile_local_files(self, tester_login):
        """Tests that we can upload all of cb_compile_tester's projects
        (stored locally in test_data/cb_compile_tester), compile them,
        and finally delete them."""

        WebDriverWait(self.driver, 30).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "#home-page-loading-screen")
                )
            )

        filenames = os.listdir(COMPILE_TESTER_DIR)
        test_files = [os.path.join(COMPILE_TESTER_DIR, name) for name in filenames]

        for test_file in test_files:
            # Click the Upload Sketch button.
            upload_button = self.get_element(By.CSS_SELECTOR, '#sketch-upload-button')
            upload_button.click()
            # Click the Upload zip option from the dropdown menu.
            sketch_upload_zip = self.get_element(By.CSS_SELECTOR, '#upload-sketch-zip')
            sketch_upload_zip.click()

            upload_name = self.upload_project('#dropzoneForm',
                                             test_file,
                                             os.path.splitext(os.path.basename(test_file))[0])
            # Wait for the success mark to appear.
            WebDriverWait(self.driver, 30).until(
                expected_conditions.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".dz-success-mark")
                )
            )
            # Close the modal.
            close_btn = self.get_element(By.CSS_SELECTOR, "#home-upload-sketch-modal .btn-danger")
            close_btn.click()
            # Wait for the modal to close.
            WebDriverWait(self.driver, 30).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".modal-backdrop fade")
                )
            )
            selector = '#project_list li[data-name="'+ upload_name +'"]'
            project_uploaded = self.get_element(By.CSS_SELECTOR, selector).text.split('\n')[0]
            assert upload_name != project_uploaded, "upload_name is different from project_uploaded!"

        flag = True
        while flag:
            uploaded_sketches = self.get_elements(By.CSS_SELECTOR, '#project_list > li')
            if len(uploaded_sketches) >= len(test_files):
                flag = False
                break
            time.sleep(1)
        self.compile_all_sketches(COMPILE_TESTER_STAGING_URL,
            '#user_projects tbody a',
            iframe=False,
            compile_type='sketch',
            create_report=True, logfile=COMPILE_TESTER_LOGFILE_STAGING)

        for name in filenames:
            name = name.split('.')[0]
            self.delete_project(name.replace(" ", "-"))
