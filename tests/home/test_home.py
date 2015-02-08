from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.keys import Keys

class TestHome(SeleniumTestCase):

    def test_navigate_home(self):
        #self.open("/")
        driver = self.driver
        driver.get("https://codebender.cc")
        assert "codebender" in self.driver.title

    def test_login(self):
        """tests to ensure the login box is displayed"""
        driver = self.driver
        #self.open("/")
        driver.get("https://codebender.cc")
        login_elem = driver.find_element_by_id("login_btn")    #finds login button
        login_elem.send_keys(Keys.RETURN)                      #clicks login button
        logbox_elem = driver.find_element_by_id("login_box")   #finds login div
        assert logbox_elem.is_displayed()                      #checks to see if div is visible

    def test_slider(self):
        """ tests slider bullets, play, and pause """
        driver = self.driver

        # define bullets
        bullet_one = driver.find_element_by_link_text('1')
        bullet_two = driver.find_element_by_link_text('2')
        bullet_three = driver.find_element_by_link_text('3')
        bullet_four = driver.find_element_by_link_text('4')
        bullet_five = driver.find_element_by_link_text('5')

        # make sure initial slider view is shown
        init_boxport = driver.find_element_by_xpath("//div[@class='bx-viewport']/ul/li/div[@class='row-fluid']")
        assert init_boxport.is_displayed()

        # test functionality of second bullet 
        aghard_link = driver.find_element_by_xpath("//div[@class='row-fluid']/div[@class='span8']/p/a")
        assert not aghard_link.is_displayed()
        bullet_two.click()
        assert aghard_link.is_displayed()

    def test_browser_quit(self):
        """ closes browser completely  """
        driver = self.driver
        driver.quit()





