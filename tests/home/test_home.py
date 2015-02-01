from codebender_testing.utils import SeleniumTestCase


class TestHome(SeleniumTestCase):

    def test_navigate_home(self):
        self.driver.get("http://localhost")
        assert "Codebender" in self.driver.title

