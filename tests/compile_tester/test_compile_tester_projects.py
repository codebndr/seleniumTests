import os

import pytest

from codebender_testing.config import BASE_URL
from codebender_testing.config import COMPILE_TESTER_DIR
from codebender_testing.config import COMPILE_TESTER_LOGFILE
from codebender_testing.config import COMPILE_TESTER_URL
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.utils import temp_copy


class TestCompileTester(SeleniumTestCase):

    # Here, we require the LIVE_SITE_URL since the compiler tester user
    # does not exist in the bachelor version.
    @pytest.mark.requires_url(LIVE_SITE_URL)
    def test_compile_all_user_projects(self):
        """Tests that all library examples compile successfully."""
        self.compile_all_sketches(COMPILE_TESTER_URL, '#user_projects tbody a',
            iframe=True, log_file=COMPILE_TESTER_LOGFILE)

    # Here we require BASE_URL since cb_compile_tester's projects are already
    # uploaded to the live site.
    @pytest.mark.requires_url(BASE_URL)
    def test_compile_local_files(self, tester_login):
        """Tests that we can upload all of cb_compile_tester's projects
        (stored locally in test_data/cb_compile_tester), compile them,
        and finally delete them."""
        test_files = [os.path.join(COMPILE_TESTER_DIR, name)
            for name in next(os.walk(COMPILE_TESTER_DIR))[2]]
        projects = [self.upload_project(fname) for fname in test_files]
        project_names, project_urls = zip(*projects)

        self.compile_sketches(project_urls, logfile=COMPILE_TESTER_LOGFILE)
        for name in project_names:
            self.delete_project(name)

