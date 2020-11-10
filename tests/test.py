#!/usr/bin/env python3
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.driver = webdriver.Chrome('/home/jarek/hddskrypty/python/selenium/chromedriver')
        try:
            cls.driver.get("https://listjj.herokuapp.com")
            WebDriverWait(cls.driver,5).until(EC.presence_of_element_located((By.ID,"id_username")))
        finally:
            username = cls.driver.find_element_by_id('id_username')
            username.send_keys("jarek")
            password = cls.driver.find_element_by_id('id_password')
            password.send_keys("her.Inferno9")
            password.send_keys(Keys.ENTER)

    @classmethod
    def tearDown(cls):
            cls.driver.close()


class TestListJJ(BaseTestCase):    
    def test_add_note(self):
        try:
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.ID,"id_description")))
        finally:
            new_note_input = self.driver.find_element_by_id('id_description')
            new_note_input.send_keys("test_note_jj")
            self.driver.find_element_by_xpath("//button[@type='submit']").click()
            assert "test_note_jj" in self.driver.page_source

    def test_delete_note(self):
        try:
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.ID,"id_description")))
        finally:
            self.driver.find_element_by_xpath("(//button[@type='submit'])[18]").click()
            assert "test_note_jj" not in self.driver.page_source


if __name__ == "__main__":
    unittest.main()

# test = TestListJJ()
# test.login()
# test.add_note()


#driver.close()
