from codebender_testing.config import STAGING_SITE_URL
from selenium.webdriver.common.by import By
from codebender_testing.utils import SeleniumTestCase


class TestDeleteAllSketches(SeleniumTestCase):

    def test_delete(self, tester_login):
        try:
            sketches = self.find_all('#project_list > li .sketch-block-title > a')
            projects = []
            for sketch in sketches:
                projects.append(sketch.text)
            for project in projects:
                self.delete_project(project)
        except:
            print 'No sketches found'
