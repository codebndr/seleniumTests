from codebender_testing.utils import CodebenderEmbeddedTestCase
import re


EMBEDDED_VIEWS = [
    'http://blog.codebender.cc/2014/03/07/lesson-1-inputs-and-outputs/',
    'https://www.sparkfun.com/news/1803',
    'http://1sheeld.com/blog/announcing-4-new-shields-tasker-integration-partnership-with-codebender/',
    'http://edu.olympiacircuits.com/codebender.html',
    'http://redbearlab.com/quick-start-codebender/',
    'https://tiny-circuits.com/tinyscreen',
    'http://lowpowerlab.com/programming/',
    'http://lowpowerlab.com/blog/2014/12/03/moteino-now-on-codebender-cc/',
    'http://microview.io/intro/getting-started.html',
    'http://www.hummingbirdkit.com/learning/arduino-programming'
]


class TestHome(CodebenderEmbeddedTestCase):

    def test_embedded_views(self):
        embed_sketch_re = re.compile('^https:\/\/codebender\.cc\/embed\/sketch:\d+$')
        example_re = re.compile('^https:\/\/codebender\.cc\/example\/.+$$')
        serial_monitor_re = re.compile('^https:\/\/codebender\.cc\/embed\/serialmonitor$$')
        for embedded in EMBEDDED_VIEWS:
            self.open(embedded)
            iframes = self.driver.find_elements_by_tag_name('iframe')
            test_iframes = []
            for iframe in iframes:
                iframe_src = iframe.get_attribute('src')
                if embed_sketch_re.match(iframe_src):
                    self.test_embedded_sketch(iframe_src)
