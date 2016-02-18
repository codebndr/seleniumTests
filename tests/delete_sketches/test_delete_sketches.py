from codebender_testing.config import STAGING_SITE_URL
from selenium.webdriver.common.by import By
from codebender_testing.utils import SeleniumTestCase
import pytest

class TestDeleteAllSketches(SeleniumTestCase):

    @pytest.mark.requires_url(STAGING_SITE_URL)
    def test_delete(self, tester_login):
        sketches = self.driver.find_elements(By.CSS_SELECTOR, '#project_list > li >a')
        projects = []
        for sketch in sketches:
            projects.append(sketch.text)
        for project in projects:
            self.delete_project(project)
