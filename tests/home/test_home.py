from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.keys import Keys

class TestHome(SeleniumTestCase):

    def test_navigate_home(self):
        self.open("/")
        assert "Codebender" in self.driver.title

    #tests login features
    def test_login(self):
        driver = self.driver
        self.open("/")
        login_elem = driver.find_element_by_id("login_btn")    #finds login button
        login_elem.send_keys(Keys.RETURN)                      #clicks login button
        logbox_elem = driver.find_element_by_id("login_box")   #finds login div
        assert logbox_elem.is_displayed()                      #checks to see if div is visible
