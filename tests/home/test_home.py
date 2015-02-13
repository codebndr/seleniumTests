from codebender_testing.config import TEST_CREDENTIALS
from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.keys import Keys

class TestHome(SeleniumTestCase):

    def test_navigate_home(self):
        """ opens browser to codebender bachelor """
        self.open("/")
        assert "Codebender" in self.driver.title

    def test_login(self):
        driver = self.driver
        self.open("/")

        """ tests to ensure login div appears """        
        login_elem = driver.find_element_by_id("login_btn")    #finds login button
        login_elem.send_keys(Keys.RETURN)                      #clicks login button
        logbox_elem = driver.find_element_by_id("login_box")   #finds login div
        assert logbox_elem.is_displayed()                      #checks to see if div is visible

        """ tests login with invalid username """
        # define elements in login form 
        username_elem = driver.find_element_by_id("username")
        password_elem = driver.find_element_by_id("password")
        submit_elem = driver.find_element_by_id("_submit")
        
        # enter invalid username with correct password
        username_elem.send_keys("codebender")
        password_elem.send_keys(TEST_CREDENTIALS['password'])
        submit_elem.click()

        # check for error message
        error_elem = driver.find_element_by_class_name('text-error')
        assert error_elem.is_displayed() 

    def test_quit(self):
        """ closes driver """
        driver = self.driver
        driver.quit()













