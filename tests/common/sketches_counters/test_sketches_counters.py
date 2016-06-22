from codebender_testing.utils import SeleniumTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class TestSketchesCounters(SeleniumTestCase):
    
    def test_sketches_counters(self):
	self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://staging.codebender.cc/"
        self.verificationErrors = []
        self.accept_next_alert = True
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("login_btn").click()
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys("demo_user")        
	driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("testerPASS")
        driver.find_element_by_id("_submit").click()
        driver.find_element_by_id("create_sketch_btn").click()


        driver.find_element_by_id("create-sketch-modal-action-button").click()
	time.sleep(5)
        driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
	time.sleep(5)        
	driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_xpath("(//input[@name='create-sketch-modal-title'])[2]").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        time.sleep(5)
	driver.find_element_by_id("logo_small").click()
        driver.find_element_by_id("create_sketch_btn").click()
        driver.find_element_by_xpath("(//input[@name='create-sketch-modal-title'])[2]").click()
        driver.find_element_by_id("create-sketch-modal-action-button").click()
        time.sleep(5)
	driver.find_element_by_id("logo_small").click()
	assert driver.find_element_by_id("private-sketches-counter").text=="2"
	assert driver.find_element_by_id("public-sketches-counter").text=="2"        
	assert driver.find_element_by_id("privateProjectAvailableNumber").text=="0"	        
	assert driver.find_element_by_id("available-private-projects-counter").text=="0/2"
	assert "Add more"==driver.find_element_by_link_text("Add more").text

	#Private-->Public
        driver.find_element_by_link_text("Edit Info").click()
	time.sleep(5)
        driver.find_element_by_name("edit-sketch-modal-title").click()
        driver.find_element_by_id("edit-sketch-modal-action-button").click()
	time.sleep(5)
	assert driver.find_element_by_id("private-sketches-counter").text=="1"
	assert driver.find_element_by_id("public-sketches-counter").text=="3" 

	#Public-->Private
        driver.find_element_by_link_text("Edit Info").click()
	time.sleep(5)
        driver.find_element_by_xpath("(//input[@name='edit-sketch-modal-title'])[2]").click()
        driver.find_element_by_id("edit-sketch-modal-action-button").click()
     	time.sleep(5)
        assert driver.find_element_by_id("private-sketches-counter").text=="2"
	assert driver.find_element_by_id("public-sketches-counter").text=="2" 
	#for x in range(0, 3):
	#	driver.find_element_by_css_selector("i.fa.fa-trash").click()
	#	driver.find_element_by_css_selector("div.modal-footer.delete-sketch-modal-footer > button.btn.delete-sketch-modal-button").click()
		#driver.find_element_by_css_selector("div.modal-footer.delete-sketch-modal-footer > button.btn.btn-danger").click()



	driver.find_element_by_id("logout").click()
    
 


