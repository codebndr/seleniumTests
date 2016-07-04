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

class TestEditor(SeleniumTestCase):

    def test_editor(self):
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

        #Check that when you click on the sketch, sketch opens in editor.
        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        assert self.get_element(By.ID, "cb_cf_flash_btn").text == "Run on Arduino"

        #double click the earth icon on the left of its title to make it private .
        #Project privacy settings successfully changed!
        changeButton = self.get_element(By.XPATH, "//span[@id='editor_heading_privacy_icon']/i")
        actions = ActionChains(driver)
        actions.move_to_element(changeButton)
        actions.double_click(changeButton)
        actions.perform()
        self.get_element(By.ID, "logo_small").click()
        assert self.get_element(By.ID, "public-sketches-counter").text=="0"
        assert self.get_element(By.ID, "private-sketches-counter").text=="1"

        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        changeButton = self.get_element(By.XPATH, "//span[@id='editor_heading_privacy_icon']/i")
        actions = ActionChains(driver)
        actions.move_to_element(changeButton)
        actions.double_click(changeButton)
        actions.perform()

        #Go to a sketch in editor and change the short description
        #Rename the sketch from the editor
        driver.find_element_by_xpath("//div[2]/a/span").click()
        driver.find_element_by_xpath("//div[6]/div[2]/div/div/input").clear()
        driver.find_element_by_xpath("//div[6]/div[2]/div/div/input").send_keys("test")
        driver.find_element_by_xpath("//div[3]/button[2]").click()
        #assert self.get_element(By.XPATH, "//div/pre").text == "Name successfully changed!"
        driver.find_element_by_xpath("//div[6]/div/button").click()

        #Go to a sketch in editor and click the Clone button
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        driver.find_element_by_id("logo_small").click()
        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        driver.find_element_by_id("clone_btn").click()
        driver.find_element_by_id("logo_small").click()

        #Go to a sketch in editor and add a file/Rename file/delete a file/
        driver.find_element_by_id("newfile").click()
        driver.find_element_by_id("createfield").clear()
        driver.find_element_by_id("createfield").send_keys("test")
        driver.find_element_by_id("createbutton").click()
        self.get_element(By.XPATH, "//ul[@id='files_list']/li[2]/a[3]/i").click()
        driver.find_element_by_id("newFilename").clear()
        driver.find_element_by_id("newFilename").send_keys("testA")
        driver.find_element_by_id("renamebutton").click()
        self.get_element(By.XPATH, "//ul[@id='files_list']/li[2]/a[2]/i").click()
        self.get_element(By.XPATH, "//div[5]/div[3]/a[2]").click()
        driver.find_element_by_id("logo_small").click()

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
