from selenium.webdriver.common.by import By
import pytest

from codebender_testing.config import TESTS_USER_AGENT
from codebender_testing.utils import SeleniumTestCase
from codebender_testing.utils import SELECT_BOARD_SCRIPT


TEST_BOARD = 'Arduino Uno'


class TestUserHome(SeleniumTestCase):

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
        if 'Linux' in TESTS_USER_AGENT:
            self.get_element(By.CSS_SELECTOR, '#linux-directions .btn:nth-child(2)').click()
        elif 'Windows' in TESTS_USER_AGENT:
            self.get_element(By.CSS_SELECTOR, '#windows-directions .btn:nth-child(2)').click()
        elif 'Mac' in TESTS_USER_AGENT:
            self.get_element(By.CSS_SELECTOR, '#mac-directions .btn:nth-child(2)').click()

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
        cb_cf_operation_output = self.get_element(By.CSS_SELECTOR, '#cb_cf_operation_output')
        assert cb_cf_operation_output.text.strip() == 'Please select a valid port!'
        board_image = self.get_element(By.CSS_SELECTOR, '#arduinoImg')
        assert board_image.is_displayed()

    def test_page_5(self):
        """Test page 5"""
        pass
