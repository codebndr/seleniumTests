from codebender_testing.config import TEST_CREDENTIALS
from codebender_testing.utils import CodebenderIframeTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestHome(CodebenderIframeTestCase):
    def test_blog(self):
        """ tests codebender's blog """
        self.open('http://blog.codebender.cc/2014/03/07/lesson-1-inputs-and-outputs/')

        assert "Lesson 1: Inputs and Outputs | codebender's blog" in self.driver.title

        iframe = {
            'project_name': "Lesson 1 Analog Inputs Example",
            'user_name': "codebender_tutorials",
            'sketch_contents': "// Dummy example on reading Analog Inputs"
        }

        self.get_iframe('iframe[src="https://codebender.cc/embed/sketch:31583"]', iframe)

    def test_sparkfun(self):
        """tests sparkfun"""
        self.open('https://www.sparkfun.com/news/1803')

        iframe = {
            'project_name': "SIK_circuit01_blink",
            'user_name': "SparkFun SIK Examples",
            'sketch_contents': "/* SparkFun Inventor's Kit"
        }

        self.get_iframe('iframe[src="https://codebender.cc/embed/sketch:77046"]', iframe)

    def test_oneshield(self):
        """tests one shield"""
        self.open('http://1sheeld.com/blog/announcing-4-new-shields-tasker-integration-partnership-with-codebender/')

        iframe = {
            'project_name': "VoiceRecognition",
            'user_name': None,
            'sketch_contents': "/*"
        }

        self.get_iframe('iframe[src="https://codebender.cc/embed/example/OneSheeld/VoiceRecognition"]', iframe)
