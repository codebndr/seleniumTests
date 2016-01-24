from codebender_testing.config import COMPILE_TESTER_DIR
from codebender_testing.config import COMPILE_TESTER_LOGFILE
from codebender_testing.config import COMPILE_TESTER_URL
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.config import STAGING_SITE_URL
from codebender_testing.config import COMPILE_TESTER_STAGING_URL
from codebender_testing.config import SOURCE_BACHELOR
from codebender_testing.config import TIMEOUT
from selenium.webdriver.common.by import By
from codebender_testing.utils import SeleniumTestCase
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
        filenames = next(os.walk(COMPILE_TESTER_DIR))[2]
        test_files = [os.path.join(COMPILE_TESTER_DIR, name) for name
            in next(os.walk(COMPILE_TESTER_DIR))[2]]
        projects = [self.upload_project('#uploadFolderZip form', fname,
            os.path.splitext(os.path.basename(fname))[0]) for fname
            in test_files]
        flag = True
        while flag:
            uploaded_sketches = self.get_elements(By.CSS_SELECTOR, '#project_list > li')
            if len(uploaded_sketches) >= len(projects):
                flag = False
                break
            time.sleep(1)
        self.compile_all_sketches(COMPILE_TESTER_STAGING_URL,
            '#user_projects tbody a',
            iframe=False,
            compile_type='sketch',
            create_report=True, logfile=COMPILE_TESTER_LOGFILE)
        for name in projects:
            self.delete_project(name.replace(" ", "-"))
