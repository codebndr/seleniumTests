from codebender_testing.config import COMPILE_TESTER_DIR
from codebender_testing.config import COMPILE_TESTER_LOGFILE
from codebender_testing.config import COMPILE_TESTER_URL
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.config import SOURCE_BACHELOR
from codebender_testing.utils import SeleniumTestCase
import os
import pytest


class TestCompileTester(SeleniumTestCase):

    # Here, we require the LIVE_SITE_URL since the compiler tester user
    # does not exist anywhere else.
    @pytest.mark.requires_url(LIVE_SITE_URL)
    def test_compile_all_user_projects(self):
        """Tests that all user's sketches compile successfully."""
        self.compile_all_sketches(COMPILE_TESTER_URL, '#user_projects tbody a',
            iframe=True, logfile=COMPILE_TESTER_LOGFILE,
            compile_type='sketch', create_report=True)
