from codebender_testing.utils import SeleniumTestCase


class TestHome(SeleniumTestCase):

    def test_navigate_home(self):
        self.open("/")
        assert "Codebender" in self.driver.title

