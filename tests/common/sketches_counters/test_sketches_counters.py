from codebender_testing.utils import SeleniumTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from codebender_testing import config
from codebender_testing.config import STAGING_SITE_URL
from selenium.webdriver.common.action_chains import ActionChains
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

        #Create 2 public sketches and Create 2 private sketches
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_xpath("(//input[@name='create-sketch-modal-title'])[2]").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_xpath("(//input[@name='create-sketch-modal-title'])[2]").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()

        #Check that the counters have the correct value.
        assert driver.find_element_by_id("private-sketches-counter").text=="2"
        assert driver.find_element_by_id("public-sketches-counter").text=="2"

        #Check that the counter for private projects also appears at the Badges section and has the correct value.
        assert driver.find_element_by_id("privateProjectAvailableNumber").text=="0"
        assert driver.find_element_by_id("available-private-projects-counter").text=="0/2"

        #Check that if your account has private projects (e.g. 2) and all yor projects are public, counter for available private sketches should be 0/number of total private sketches(e.g. 		0/2) and the link to the private sketches should be Add more.
        assert "Add more" == driver.find_element_by_link_text("Add more").text

        #ToDo Check that the number of private projects available is updated each time that you make a change
        #(e.g from private to public and vice versa).
        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        changeButton = self.get_element(By.XPATH, "//span[@id='editor_heading_privacy_icon']/i")
        actions = ActionChains(driver)
        actions.move_to_element(changeButton)
        actions.double_click(changeButton)
        actions.perform()
        self.get_element(By.ID, "logo_small").click()
        assert self.get_element(By.ID, "public-sketches-counter").text=="3"
        assert self.get_element(By.ID, "private-sketches-counter").text=="1"

        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        changeButton = self.get_element(By.XPATH, "//span[@id='editor_heading_privacy_icon']/i")
        actions = ActionChains(driver)
        actions.move_to_element(changeButton)
        actions.double_click(changeButton)
        actions.perform()
        self.get_element(By.ID, "logo_small").click()
        assert driver.find_element_by_id("public-sketches-counter").text=="2"
        assert driver.find_element_by_id("private-sketches-counter").text=="2"


        #Check that All, Public and Private buttons work, clicking on each of them and verifying
        #that the correct number of sketches is viewed each time

        #Check "All button"
        self.get_element(By.XPATH, "//div[@id='filter-options']/label[2]").click()
        sketches = self.find_all('#project_list >li')
        assert len(sketches) == 4
        #Check "Public button"
        self.get_element(By.XPATH, "//div[@id='filter-options']/label[2]").click()
        sketches = self.find_all('#project_list >li .cb-icon-globe-inv')
        assert len(sketches) == 2
        #Check "Private button"
        self.get_element(By.XPATH, "//div[@id='filter-options']/label[3]").click()
        sketches = self.find_all('#project_list >li .fa-lock')
        assert len(sketches) == 2

        #Check that the counter for available private sketches also appears at the upload sketch modal (ino, zip, multiple zip) and at the create and edit sketch modal.
        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-ino").click()
        assert self.get_element(By.ID, "upload-sketch-modal-available-private-projects").text == "0/2"
        driver.find_element_by_xpath("//div[4]/div[3]/button").click()

        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-zip").click()
        assert self.get_element(By.ID, "upload-sketch-modal-available-private-projects").text == "0/2"
        driver.find_element_by_xpath("//div[4]/div[3]/button").click()

        self.get_element(By.ID, "sketch-upload-button").click()
        self.get_element(By.ID, "upload-sketch-folder-zip").click()
        assert self.get_element(By.ID, "upload-sketch-modal-available-private-projects").text == "0/2"
        driver.find_element_by_xpath("//div[4]/div[3]/button").click()

        self.get_element(By.ID, "create_sketch_btn").click()
        assert self.get_element(By.ID, "create-sketch-modal-available-private-projects").text == "0/2"
        driver.find_element_by_xpath("//button[2]").click()

        #Open the create sketch modal and try to create a new project without providing a name.
        #The Create button should be disabled.
        self.get_element(By.ID, "create_sketch_btn").click()
        self.get_element(By.ID, "create-sketch-name").clear()
        self.get_element(By.ID, "create-sketch-name").send_keys(Keys.CONTROL + "a")
        self.get_element(By.ID, "create-sketch-name").send_keys(Keys.DELETE)
        assert not self.get_element(By.ID, "create-sketch-modal-action-button").is_enabled()
        driver.find_element_by_xpath("//button[2]").click()


        #Check that sketch name is auto-generated as: Untitled Sketch CURRENT_DATE.
        self.get_element(By.ID, "create_sketch_btn").click()
        current_date_text= "Untitled Sketch " + time.strftime("%Y-%m-%d")
        assert self.get_element(By.ID, "create-sketch-name").get_attribute("value") == current_date_text
        driver.find_element_by_xpath("//button[2]").click()

        #Check that when you create the sketch you are redirected into the editor.
        self.get_element(By.ID, "create_sketch_btn").click()
        self.get_element(By.ID, "create-sketch-modal-action-button").click()
        self.get_element(By.ID, "cb_cf_flash_btn")
        self.get_element(By.ID, "logo_small").click()

        #Check that short description
        #Write short description with 17 characters
        self.get_element(By.ID, "create_sketch_btn").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").send_keys("short description")
        assert self.get_element(By.ID, "create-sketch-modal-sort-description-count").text == "123"
        driver.find_element_by_xpath("//button[2]").click()

        #Write short description with 140 characters
        self.get_element(By.ID, "create_sketch_btn").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").send_keys("shortdescriptionshortdescriptionshortdescriptionshortdescriptionshortdescriptionshortdescriptionshortdescriptionshortdescriptionshortdescrip")
        assert self.get_element(By.ID, "create-sketch-modal-sort-description-count").text == "0"
        driver.find_element_by_xpath("//button[2]").click()

        #Write short description with 153 characters
        self.get_element(By.ID, "create_sketch_btn").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").click()
        self.get_element(By.ID, "create-sketch-modal-sort-description").send_keys("short descriptionshort descriptionshort descriptionshort descriptionshort descriptionshort descriptionshort descriptionshort descriptionshort description")
        assert self.get_element(By.ID, "create-sketch-modal-sort-description-count").text == "-13"
        assert self.get_element(By.ID, "create-sketch-modal-sort-description-count").value_of_css_property('color') == "rgba(255, 0, 0, 1)"
        driver.find_element_by_xpath("//button[2]").click()

class TestCloneSketch(SeleniumTestCase):

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

    def test_clone(self):
        #Create Clone
        self.get_element(By.ID,"create_sketch_btn").click()
        self.get_element(By.ID,"create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        self.get_element(By.ID,"logo_small").click()
        self.get_element(By.XPATH, "//div[4]/a[2]/i").click()
        self.get_element(By.ID, "save")
        self.get_element(By.ID,"logo_small").click()
        current_date_text= "Untitled Sketch " + time.strftime("%Y-%m-%d")
        assert self.get_element(By.XPATH, "//div[4]/div/span").text == "Cloned from Sketch"
        assert self.get_element(By.XPATH, "//div[4]/div/a").text == current_date_text
        assert self.get_element(By.XPATH, "//div[4]/div/a[2]").text == "demo_user"

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
