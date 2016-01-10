from codebender_testing.config import LIBRARIES_FETCH_LOGFILE
from codebender_testing.utils import SeleniumTestCase


class TestLibraryExamples(SeleniumTestCase):

    def test_open_all_libraries(self):
        """Tests that all libraries and examples open successfully."""
        self.open_all_libraries_and_examples('/libraries', LIBRARIES_FETCH_LOGFILE)
