from codebender_testing.utils import SeleniumTestCase
from selenium.webdriver.common.by import By

# Global variables
ERROR_MESSAGE = 'Oops! Something seems to be broken :/'
ROUTES_404 = [
    '/hello',
    '/foo',
    '/bar'
]

class Test404Page(SeleniumTestCase):
    def test_404_page(self, testing_url):
        """
        Test for 404 error page.
        Visits URLs registered at ROUTES_404 and verifies that the 404 error page opens
        """

        for url in ROUTES_404:
            self.open(url)
            logo = self.get_element(By.CSS_SELECTOR, '.brand')
            assert logo.get_attribute('href')[:-1] == self.site_url # check href attribute of .brand

            error_message = self.get_element(By.CSS_SELECTOR, '.container-fluid .span12 .span12 h1')
            assert error_message.text.strip() ==  ERROR_MESSAGE # check text value of error message h1
