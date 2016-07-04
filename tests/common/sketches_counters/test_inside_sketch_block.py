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

class TestInsideSketchBlock(SeleniumTestCase):

    def test_inside_sketch_block(self):
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

        assert driver.find_element_by_id("public-sketches-counter").text=="0"

        #Create 1 public sketches
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        self.get_element(By.ID, "save")
        driver.find_element_by_id("logo_small").click()
        #Check that the sketch was created
        assert driver.find_element_by_id("public-sketches-counter").text=="1"

        #Check that when you click on the sketch, sketch opens in editor.
        #Create a sketch using the Create button and go back to homepage.
        #Sketch should say Created instead of Modified.
        #Go back to the sketch previously created and do some changes.
        #Save it and go back to homepage. Sketch should say Modified instead of Created.
        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        assert self.get_element(By.ID, "cb_cf_flash_btn").text == "Run on Arduino"
        self.get_element(By.ID, "logo_small").click()
        assert self.get_element(By.XPATH , "//div/a/span").text == "created a few seconds ago"

        driver.find_element_by_xpath("//li/div/div/div[2]/a").click()
        self.get_element(By.ID, "save").click()
        self.get_element(By.ID, "logo_small").click()
        assert self.get_element(By.XPATH , "//div/a/span").text == "modified a few seconds ago"

        #Check the Share button.
        driver.find_element_by_xpath("//div[4]/a/i").click()
        driver.find_element_by_link_text("Share").click()
        driver.find_element_by_link_text("Embed").click()
        driver.find_element_by_link_text("Share").click()
        assert self.get_element(By.XPATH , "//div[7]/div/h3").text == "Share your Sketch"
        self.get_element(By.XPATH, "//div[@id='share-modal']/div/button").click()

        #Check the clone sketch function.
        #Click on Clone button and check that the sketch is cloned and opens in editor.
        self.get_element(By.XPATH, "//div[4]/a[2]/i").click()
        self.get_element(By.ID, "save").click()
        self.get_element(By.ID, "logo_small").click()
        self.get_element(By.XPATH, "//li/div/div/div[2]/a").click()
        self.get_element(By.ID, "logo_small").click()

        #Check that the file list of the sketch is at the bottom of the sketch block.
        driver.find_element_by_id("newfile").click()
        driver.find_element_by_id("createfield").clear()
        driver.find_element_by_id("createfield").send_keys("test.h")
        self.get_element(By.ID, "createbutton").click()
        assert self.get_element(By.ID, "operation_output").text == "File successfully created."
        driver.find_element_by_id("logo_small").click()

        #Check that when a sketch has a short description, it appears at the section below the name,
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-short-description").clear()
        driver.find_element_by_id("create-sketch-modal-short-description").send_keys("Test")
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        assert self.get_element(By.ID, "short-description").text == "Test"

        #Ckeck that when a sketch has a short description does not appear at all.
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-short-description").clear()
        driver.find_element_by_id("create-sketch-modal-short-description").send_keys("TestTestTestTestTestTestTestTestTestTest")
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        assert self.get_element(By.ID, "short-description").text == "TestTestTestTestTestTestTestTestTestTest"
        driver.find_element_by_id("logo_small").click()

        #Check the delete sketch fuction.
        driver.find_element_by_xpath("//a[3]/i").click()
        #Check that when the sketch is deleted the modal stays open showing the result of the deletion.
        assert self.get_element(By.XPATH, "//div[5]/div/h3").text == "Are you sure you want to delete your sketch?"
        driver.find_element_by_xpath("//div[4]/button").click()
        driver.find_element_by_xpath("//div[4]/button[2]").click()

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
