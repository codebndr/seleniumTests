from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from codebender_testing.utils import SeleniumTestCase


class TestBoards(SeleniumTestCase):

    def test_on_boards_page(self):
        """ opens browser to codebender bachelor """
        self.open("/")
        self.login()
        boards_link = self.get_element(By.LINK_TEXT, 'Supported Boards')
        boards_link.click()
        assert "boards" in self.driver.title

    def test_successful_upload(self):
        """ tests successful upload """
        driver = self.driver 
        driver.execute_script("document.getElementById('filestyle-0').style.left=0;")
        input_element = self.get_element(By.ID, 'filestyle-0')
        input_element.send_keys("/home/codebender/success.txt")
        submit_button = self.get_element(By.CLASS_NAME, 'btn-success')
        submit_button.click()
        assert "successfully added" in driver.page_source

    def test_upload_with_error(self):
        """ tests upload of file with error """
        driver = self.driver 
        driver.execute_script("document.getElementById('filestyle-0').style.left=0;")
        input_element = self.get_element(By.ID, 'filestyle-0')
        input_element.send_keys("/home/codebender/error.h")
        submit_button = self.get_element(By.CLASS_NAME, 'btn-success')
        submit_button.click()
        assert "Error" in driver.page_source

    def test_delete_board_button(self):
        """ tests button to delete a board """
        driver = self.driver
        trash_icon = self.get_element(By.XPATH, "//div/h4[1]/a/i[@class='icon-trash']")
        trash_icon.click()
        delete_board_button = self.get_element(By.ID, 'deleteBoardButton')
        delete_board_button.click()
        assert "successfully deleted" in driver.page_source

    def test_logout(self):
        """ logs out user to prepare for following tests """
        logout_button = self.get_element(By.ID, 'logout')
        logout_button.click()
