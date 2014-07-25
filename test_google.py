import re
import sys
import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import json

USERNAME = os.environ.get("USERNAME")
KEY = os.environ.get("KEY")

LOCAL_URL = "http://127.0.0.1:4444/wd/hub"
SAUCE_URL = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (USERNAME, KEY)
SELENIUM_URL = LOCAL_URL

browsers = [{'browserName':'firefox','name':'Firefox'}]

def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = type(name, (base_class,), d)
    return decorator

@on_platforms(browsers)
class GoogleImageSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor=SELENIUM_URL)
        self.driver.implicitly_wait(10)
        self.passed = False

    def test_elephant(self):
        '''Search for elephant'''

        dr = self.driver
        dr.get("http://google.com/en")

        dr.find_element_by_link_text("Images").click()
        dr.find_element_by_xpath("//a[@aria-label='Search by image']").click()

        dr.find_element_by_link_text("Upload an image").click()
        el = dr.find_element_by_xpath("//input[@name='encoded_image']")
        el.send_keys(os.getcwd()+"/image.jpg")

        dr.find_element_by_xpath("//*[@id='search']//a[contains(.,'слон') " \
                                 "or contains(.,'elephant')]").click()

        page_text = dr.find_element_by_tag_name('body').text
        self.assertRegex(page_text, re.compile('(слон|elephant)',re.I))
        self.passed = True

    def tearDown(self):
        if SAUCE_URL == SELENIUM_URL:
            self.sauce_send_result(self.passed)
        self.driver.quit()

    def sauce_send_result(self,result):
        '''Send the result to SauceLabs'''

        url = 'http://saucelabs.com/rest/v1/%s/jobs/%s' % (USERNAME,self.driver.session_id)
        data = json.dumps({'passed':result})
        try:
            requests.put(url,data,auth=(USERNAME,KEY),headers={'Connection':'close'})
        except:
            False

if __name__ == "__main__":
    unittest.main()
