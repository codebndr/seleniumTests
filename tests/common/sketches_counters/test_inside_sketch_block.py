from codebender_testing.utils import SeleniumTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from codebender_testing import config
from codebender_testing.config import STAGING_SITE_URL
import os
import time
import pytest

class TestSketchesCounters(SeleniumTestCase):

    def test_sketches_counters(self):
        self.driver.implicitly_wait(30)
        driver = self.driver
        self.open("/")
        #Login and visit the new home page.
        credentials = {
            'username': os.environ.get('CODEBENDER_TEST_USER'),
            'password': os.environ.get('CODEBENDER_TEST_PASS'),
        }
        driver.find_element_by_id("login_btn").click()
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(credentials['username'])
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(credentials['password'])
        driver.find_element_by_id("_submit").click()

        assert driver.find_element_by_id("private-sketches-counter").text=="0"
        assert driver.find_element_by_id("public-sketches-counter").text=="0"

        #Create 1 public sketches
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()

        #Check that the sketch was created
        assert driver.find_element_by_id("public-sketches-counter").text=="1"

class TestDeleteAllSketches(SeleniumTestCase):

    @pytest.mark.requires_url(STAGING_SITE_URL)
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

        self.logout()
