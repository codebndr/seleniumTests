from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from codebender_testing import config
import os

class TestHome(SeleniumTestCase):

    def test_navigate_home(self, tester_logout):
        """ opens browser to codebender bachelor """
        self.open("/")
        assert "codebender" in self.driver.title

    def test_login(self, tester_logout):
        credentials = {
            'username': os.environ.get('CODEBENDER_TEST_USER', config.TEST_CREDENTIALS['username']),
            'password': os.environ.get('CODEBENDER_TEST_PASS', config.TEST_CREDENTIALS['password']),
        }
        driver = self.driver
        self.open("/")

        """ tests to ensure login div appears """
        login_elem = self.get_element(By.ID, "login_btn")    #finds login button
        login_elem.send_keys(Keys.RETURN)                      #clicks login button
        logbox_elem = self.get_element(By.ID, "login_box")   #finds login div
        assert logbox_elem.is_displayed()                      #checks to see if div is visible

        """ tests login with invalid username """
        # define elements in login form
        username_elem = self.get_element(By.ID, "username")
        password_elem = self.get_element(By.ID, "password")
        submit_elem = self.get_element(By.ID, "_submit")

        # enter invalid username with correct password
        username_elem.send_keys("asdfghjklpoiuytrewqzxcvbnm")
        password_elem.send_keys('1234567890')
        submit_elem.click()

        # check for error message
        error_elem = self.get_element(By.CLASS_NAME, 'text-error')
        assert error_elem.is_displayed()
        assert error_elem.text.strip() == 'Invalid username or password'

        """ tests login with invalid password """
        # refresh page so error message no longer visible
        driver.refresh()

        # re-click on login button
        login_elem = self.get_element(By.ID, "login_btn")
        login_elem.send_keys(Keys.RETURN)

        # re-define elements in login form
        username_elem = self.get_element(By.ID, "username")
        password_elem = self.get_element(By.ID, "password")
        submit_elem = self.get_element(By.ID, "_submit")

        # enter correct username with invalid password
        username_elem.clear()
        username_elem.send_keys(credentials['username'])
        password_elem.send_keys(1234567890)
        submit_elem.click()

        # re-define error message element and test
        error_elem = self.get_element(By.CLASS_NAME, 'text-error')
        assert error_elem.is_displayed()
        assert error_elem.text.strip() == 'Invalid username or password'

        """ tests that login takes you to user's home """
        # refresh page so error message no longer visible
        driver.refresh()

        # re-click on login button
        login_elem = self.get_element(By.ID, "login_btn")
        login_elem.send_keys(Keys.RETURN)

        # re-define elements in login form
        username_elem = self.get_element(By.ID, "username")
        password_elem = self.get_element(By.ID, "password")
        submit_elem = self.get_element(By.ID, "_submit")

        # log in to site using correct credentials
        username_elem.clear()
        password_elem.clear()
        username_elem.send_keys(credentials['username'])
        password_elem.send_keys(credentials['password'])
        submit_elem.click()
        assert "Logged in as" in driver.page_source
