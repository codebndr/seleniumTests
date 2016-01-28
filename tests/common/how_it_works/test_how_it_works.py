import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.support.ui import WebDriverWait

# How long to wait before we give up on trying to assess the result of commands
TIMEOUT = 30

class TestHowItWorks(SeleniumTestCase):
    
    @pytest.fixture(scope="class")
    def skip_button_display (self):
        skip_button = self.driver.find_element_by_id('skip-all-steps-button')
        assert skip_button.text == "Skip all steps"

    def test_how_it_works(self, tester_logout):
        """ opens browser to codebender how_it_works """
        self.open("/how_it_works")
        assert "Blink : codebender" in self.driver.title

    def test_skip_button (self):
        skip_button = self.driver.find_element_by_id('skip-all-steps-button')
        skip_button.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".popover-title"), "That's all for now."
            )
        )
        skip_button = self.driver.find_element_by_id('skip-all-steps-button')
        skip_button.is_displayed() == False
        self.driver.refresh()
        assert "Blink : codebender" in self.driver.title

    def test_how_it_works_page_1 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-one .popover-title"), 
                "Awesome editor (1/6)"
            )
        )  
        next_button = self.find('#hiw-one .popover-content .btn-primary')
        next_button.click()

    def test_how_it_works_page_2 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-two .popover-title"), 
                "Helpful utilities (2/6)"
            )
        )  
        next_button = self.find('#hiw-two .popover-content .btn-primary')
        next_button.click()
    
    def test_how_it_works_page_3 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-three .popover-title"), 
                "Compile & Upload (3/6)"
            )
        )  
        verify_button = self.find('#cb_cf_verify_btn')
        verify_button.click()

    def test_how_it_works_page_4 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-four .popover-title"), 
                "Better error output (4/6)"
            )
        )
        insert_text = """
        var cursor_position = editor.aceEditor.getCursorPosition();
        editor.aceEditor.getSession().insert(cursor_position, ';')
        """
        self.execute_script(insert_text, "editor") 
        verify_button = self.find('#cb_cf_verify_btn')
        verify_button.click()


    def test_how_it_works_page_5 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-five .popover-title"), 
                "Share (5/6)"
            )
        )  
        next_button = self.find('#hiw-five .popover-content .btn-primary')
        next_button.click()


    def test_how_it_works_page_6 (self, skip_button_display):
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#hiw-six .popover-title"), 
                "Collaborate (6/6)"
            )
        )  
        finish_button = self.find('.popover-content .btn-primary')
        finish_button.click()

    def test_how_it_works_page_7 (self):
        skip_button = self.driver.find_element_by_id('skip-all-steps-button')
        skip_button.is_displayed() == False
        WebDriverWait(self.driver, TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, 
                '.navbar .popover:nth-child(3) .popover-title'), 
                "That's all for now."
            )
        )
