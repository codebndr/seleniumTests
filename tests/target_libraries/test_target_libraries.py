from codebender_testing.config import LIBRARIES_TEST_LOGFILE
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.config import LOGFILE_PREFIX

import pytest

LOG_FILE = LOGFILE_PREFIX.format(log_name="test_target_libraries")

GET_ALL_LIBRARIES_SCRIPT = """
    var libraries = {};
    var humanNameRegExp = /^.+\((.+)\)$/;
    $('#mycontainer').find('.library-expand-handle').map(function () {
        var libraryName = $(this).text();
        if (humanNameRegExp.test(libraryName)) {
            libraryName = libraryName.match(humanNameRegExp)[1].trim().replace(/\.h/, '');
        }
        libraries[libraryName] = $(this).parent().find('.library_link').attr('href');
    });
    return libraries;
"""

GET_LIBRARY_EXAMPLES_SCRIPT = """
    var examples = [];
    $('#mycontainer').find('.list-group .list-group-item a').map(function () {
        examples.push(this.href);
    });
    return examples;
"""


class TestLibraryExamples(SeleniumTestCase):

    def test_compile_target_libraries(self):
        targets = pytest.config.getoption("--libraries").split(',')

        self.open('/libraries')
        libraries = self.execute_script(GET_ALL_LIBRARIES_SCRIPT, '$')

        urls_to_follow = []
        for target in targets:
            if target in libraries:
                library_url = libraries[target]
                self.open(library_url)
                urls_to_follow += self.execute_script(GET_LIBRARY_EXAMPLES_SCRIPT, '$')

        if len(urls_to_follow) > 0:
            """Tests that specific library examples compile successfully."""
            self.compile_sketches(urls_to_follow,
                                    compile_type='library',
                                    iframe=False, project_view=True,
                                    create_report=True, logfile=LOG_FILE,
                                    comment=True)
