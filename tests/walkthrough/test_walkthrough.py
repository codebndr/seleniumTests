from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import pytest
import os
from codebender_testing.config import SELENIUM_BROWSER
from codebender_testing.config import TIMEOUT
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.utils import SELECT_BOARD_SCRIPT

TEST_BOARD = 'Arduino Uno'


class TestWalkthrough(SeleniumTestCase):

    @pytest.fixture(scope="class", autouse=True)
    def open_user_home(self, tester_login):
        """Makes sure we are logged in and are at the user home page
        performing any of these tests."""
        self.get_element(By.CSS_SELECTOR, '#sidebar li:nth-child(4) a').click()

    def test_page_1(self):
        """Test page 1"""
        assert 'codebender - getting started' in self.driver.title
        self.get_element(By.CSS_SELECTOR, '#supported .btn').click()

    def test_page_2(self):
        """Test page 2"""
        pass

    def test_page_3(self):
        """Test page 3"""
        user_agent = self.execute_script('return navigator.userAgent')
        platforms = ['Linux', 'Windows', 'Mac']
        for platform in platforms:
            if platform in user_agent:
                self.get_element(By.CSS_SELECTOR, '#{0}-directions .btn:nth-child(2)'.format(platform.lower())).click()

    def test_page_4(self):
        """Test page 4"""
        cb_cf_boards = self.get_element(By.CSS_SELECTOR, '#cb_cf_boards')
        assert cb_cf_boards.is_displayed()
        self.execute_script(SELECT_BOARD_SCRIPT(TEST_BOARD), '$')
        cb_cf_ports = self.get_element(By.CSS_SELECTOR, '#cb_cf_ports')
        assert cb_cf_ports.is_displayed()
        cb_cf_flash_btn = self.get_element(By.CSS_SELECTOR, '#cb_cf_flash_btn')
        assert cb_cf_flash_btn.is_displayed()
        cb_cf_flash_btn.click()
        WebDriverWait(self.driver, TIMEOUT['FLASH_FAIL']).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#cb_cf_flash_btn'))
        )
        cb_cf_operation_output = self.get_element(By.CSS_SELECTOR, '#cb_cf_operation_output')
        assert cb_cf_operation_output.text.strip() in [
            'Please select a valid port!',
            'The specified port might not be available. Please check if it is used by another application. If the problem persists, unplug your device and plug it again. More Info',
            'An error occurred while connecting to your device. Please try again.'
        ]
        board_image = self.get_element(By.CSS_SELECTOR, '#arduinoImg')
        assert board_image.is_displayed()

    def test_page_5(self):
        """Test page 5"""
        pass
