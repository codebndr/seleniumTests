from selenium import webdriver

class TestHome:

    driver = webdriver.Firefox()

    def test_navigate_home(self):
        self.driver.get("http://localhost")
        assert "Codebender" in self.driver.title

