from codebender_testing.config import LIBRARIES_TEST_LOGFILE
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.utils import SeleniumTestCase


class TestLibraryExamples(SeleniumTestCase):

    def test_compile_all_libraries(self):
        """Tests that all library examples compile successfully."""
        self.compile_all_sketches('/libraries', '.accordion li a',
                                  logfile=LIBRARIES_TEST_LOGFILE)
