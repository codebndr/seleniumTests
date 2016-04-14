from selenium.webdriver.support.ui import WebDriverWait
import pytest
from codebender_testing.config import TEST_PROJECT_NAME
from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from urlparse import urlparse

TIMEOUT = 30

class TestAlerts(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def create_test_project(self, tester_login):
        """Makes sure we are logged in and have a project open before
        performing any of these tests."""
        self.create_sketch('private' , TEST_PROJECT_NAME, 'short description')

    @pytest.mark.does_not_require_extension
    def test_alert(self):
        operation_output = self.driver.find_element_by_id('operation_output')
        assert "To program your Arduino from your browser, install" \
        " the codebender plugin." in operation_output.text

    def test_remove_sketch(self):
        self.delete_project(TEST_PROJECT_NAME)

    @pytest.mark.does_not_require_extension
    def test_library_example(self, tester_logout):
        self.open('/libraries')
        library_example = """
        var example = $('.accordion li a').map(function(){
            { return this.href; }}).toArray();
        return example[0];
        """
        url = self.driver.execute_script(library_example)
        self.open(url)
        output = self.driver.find_element_by_id('cb_cf_operation_output')
        assert "To program your Arduino from your browser, install" \
        " the codebender plugin or app." in output.text
        flash_btn = self.find('#cb_cf_flash_btn')
        if flash_btn.is_enabled():
            assert False

    @pytest.mark.does_not_require_extension
    def test_embeded_view(self, tester_logout):
        self.open('/embed/microview_test')
        output = self.driver.find_element_by_id('cb_cf_operation_output')
        assert "To program your Arduino from your browser, install" \
        " the codebender plugin or app." in output.text
        microview_test = self.find('#microview_test')
        if microview_test.is_enabled():
            assert False

    @pytest.mark.does_not_require_extension
    def test_walkthrough_page_2(self, tester_logout):
        self.open('/static/walkthrough/page/2')
        output = self.driver.find_element_by_id('cb_cf_operation_output')
        assert "To program your Arduino from your browser, install" \
        " the codebender plugin." in output.text

    @pytest.mark.does_not_require_extension
    def test_walkthrough_page_3(self, tester_logout):
        self.open('/static/walkthrough/page/3')
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#mycontainer h1 small"),
                "Page 2 of 5"
            )
        )
        current_url = urlparse(self.driver.current_url)
        assert current_url.path == '/static/walkthrough/page/2'

    @pytest.mark.does_not_require_extension
    def test_walkthrough_page_4(self, tester_logout):
        self.open('/static/walkthrough/page/4')
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#mycontainer h1 small"),
                "Page 2 of 5"
            )
        )
        current_url = urlparse(self.driver.current_url)
        assert current_url.path == '/static/walkthrough/page/2'
