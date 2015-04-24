from codebender_testing.config import LIBRARIES_TEST_LOGFILE
from codebender_testing.config import LIVE_SITE_URL
from codebender_testing.utils import SeleniumTestCase


class TestLibraryExamples(SeleniumTestCase):

    # Only test /libraries on live site.
    # TODO: not sure if this is necessary
    @pytest.mark.requires_url(LIVE_SITE_URL)
    def test_compile_all_libraries(self):
        """Tests that all library examples compile successfully."""
        self.compile_all_sketches('/libraries', '.accordion li a',
                                  logfile=LIBRARIES_TEST_LOGFILE)
