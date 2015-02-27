from codebender_testing.config import COMPILE_TESTER_LOGFILE
from codebender_testing.config import COMPILE_TESTER_URL
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.utils import SeleniumTestCase


class TestCompileTester(SeleniumTestCase):

    # Overrides the site_url in SeleniumTestCase.
    site_url = LIVE_SITE_URL

    def test_compile_all_user_projects(self):
        """Tests that all library examples compile successfully."""
        self.compile_all_sketches(COMPILE_TESTER_URL, '#user_projects tbody a',
            iframe=True, log_file=COMPILE_TESTER_LOGFILE)

