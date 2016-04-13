from codebender_testing.config import LIBRARIES_TEST_LOGFILE
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.config import LOGFILE_PREFIX

import pytest

LOG_FILE = LOGFILE_PREFIX.format(log_name="test_target_libraries")

GET_ALL_LIBRARIES_URLS_SCRIPT = "return $('.library_link').map(function() {{ return this.href; }}).toArray();"

GET_ALL_LIBRARIES_SCRIPT = """
    var libraries = {};
    $('#mycontainer').find('.library-expand-handle').map(function () {
        var libraryName = $(this).parents('.accordion-group').attr('data-name');
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
        # Collects all libraries names.
        libraries = self.execute_script(GET_ALL_LIBRARIES_SCRIPT, '$')
        # Collects all libraries urls.
        libraries_urls = self.execute_script(GET_ALL_LIBRARIES_URLS_SCRIPT, '$')
        # List containing all the urls (libraries_urls and examples_urls) that we should comment and compile.
        urls_to_follow = []
        # List containing library's examples urls.
        library_examples_urls =[]
        library_examples_urls_dic ={}

        for target in targets:
            for url in libraries_urls:
                library_url_name=url.split('/')[-1]
                if ( library_url_name != target):
                    continue
                else:
                    library_url = url
                    # Updates urls_to_follow list with library's url.
                    urls_to_follow.append(library_url)
                    target = target.lower()
                    if target in libraries:
                        library = libraries[target]
                        self.open(library)
                        # Get library's name.
                        library_name =library.split('/')[2]
                        # Collect library's examples, if any.
                        library_examples_urls = self.execute_script(GET_LIBRARY_EXAMPLES_SCRIPT, '$')
                        # Add library with examples urls in a dictionary.
                        library_examples_urls_dic[library_name]=library_examples_urls
                        # Updates urls_to_follow list with library's examples urls.
                        urls_to_follow += self.execute_script(GET_LIBRARY_EXAMPLES_SCRIPT, '$')

        if len(urls_to_follow) > 0:
            """Tests that specific library examples compile successfully."""
            self.comment_compile_libraries_examples(urls_to_follow, library_examples_urls_dic,
                                      compile_type='target_library',
                                      iframe=False, project_view=True,
                                      create_report=True, logfile=LOG_FILE,
                                      comment=True)