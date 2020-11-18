#!/usr/bin/env python3

import unittest
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from constants import C
from page import *


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        '''Setup driver and login to page before 1st test'''
        options = Options()
        if C.HEADLESS:
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')
            options.add_argument('window-size=1366x768')

        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),
            options=options)
        cls.driver.implicitly_wait(20)
        cls.driver.set_window_position(0, 0)
        cls.driver.set_window_size(1366, 768)
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

        cls.driver.get(C.LOGIN_URL)
        cls.login_page = LoginPage(cls.driver)
        cls.note_form = NoteForm(cls.driver)
        cls.note_list_page = NoteListPage(cls.driver)
        cls.category_page = CategoryPage(cls.driver)
        cls.login_page.login(C.USERNAME, C.PASSWORD)

        cls.note_list_page.click_modify_categories_link()
        try:
            cls.category_page.click_delete_category_button()
        except NoSuchElementException:
            pass

    def test_add_delete_note(self):
        '''Test adding and deleting note'''
        self.driver.get(C.URL)
        self.note_form.type_note_description(C.NOTE_DESCRIPTION)
        self.note_form.type_note_value(C.NOTE_VALUE)
        self.note_form.click_save_note_button()
        assert self.note_list_page.page_source_matches(C.NOTE_DESCRIPTION)
        self.note_list_page.click_delete_note_button()
        assert not self.note_list_page.page_source_matches(C.NOTE_DESCRIPTION)

    @classmethod
    def setUp(cls):
        '''Setup before each test'''
        pass

    @classmethod
    def tearDown(cls):
        '''TearDown after each test'''
        pass

    @classmethod
    def tearDownClass(cls):
        '''TearDown after last test'''
        cls.driver.close()


class TestListJJ(BaseTestCase):

    def test_add_delete_category_note(self):
        '''Test adding and deleting category + note'''
        self.driver.get(C.URL)
        self.note_list_page.click_modify_categories_link()
        self.category_page.type_category_name(C.CATEGORY)
        self.category_page.click_save_category_button()
        assert self.category_page.page_source_matches(C.CATEGORY)
        self.category_page.click_set_default_category_button()
        self.driver.get(C.URL)
        assert self.note_form.is_default_category(C.CATEGORY)

        self.test_add_delete_note()

        self.note_list_page.click_modify_categories_link()
        self.category_page.click_delete_category_button()
        assert not self.category_page.page_source_matches(C.CATEGORY)


def suite():
    suite = unittest.TestSuite()
    test_methods = [
        'test_add_delete_category_note',
    ]
    for test_method in test_methods:
        suite.addTest(TestListJJ(test_method))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
