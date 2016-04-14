from codebender_testing.config import LIBRARIES_TEST_LOGFILE
from codebender_testing.utils import SeleniumTestCase

GET_SKETCHES_SCRIPT = "return $('{selector}').map(function() {{ return this.href; }}).toArray();"

GET_ALL_LIBRARIES_EXAMPLES_URLS_SCRIPT = """
var librariesMap = {};
var machineNameFilter = /.+\(\s(.+)\.h\s\)/;
var accordionHeadings = $('#mycontainer').find('.accordion-heading');
$.each(accordionHeadings, function (key, value) {{
    var libraryName = $(value).text().trim();
    if (machineNameFilter.test(libraryName)) {{
        libraryName = libraryName.match(machineNameFilter)[1].trim();
    }}
    if (!librariesMap.hasOwnProperty(libraryName)) {{
       librariesMap[libraryName] = [];
    }}

    var examples = $(value).parent().find('.accordion-body').find('li a');

    $.each(examples, function (k, v) {{
        var href = $(v).attr('href');
        librariesMap[libraryName].push(href);
    }});
}});
return librariesMap;
"""
class TestLibraryExamples(SeleniumTestCase):

    def test_compile_all_libraries(self):
        url = '/libraries'
        self.open(url)

        examples = self.execute_script(GET_SKETCHES_SCRIPT.format(selector='.accordion li a'), '$')
        assert len(examples) > 0
        libraries = self.execute_script(GET_SKETCHES_SCRIPT.format(selector='.library_link'), '$')
        assert len(libraries) > 0
        examples_libraries = examples + libraries

        """Tests that all library examples compile successfully and comments on library url page and on its examples."""
        library_examples_urls = self.execute_script(GET_ALL_LIBRARIES_EXAMPLES_URLS_SCRIPT, '$')

        self.comment_compile_libraries_examples(examples_libraries, library_examples_urls,
                                                compile_type='library', iframe=False,
                                                project_view=True, create_report=True,
                                                logfile=LIBRARIES_TEST_LOGFILE, comment=True)