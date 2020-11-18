#!/usr/bin/env python3

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from locators import *


logging.basicConfig(level=logging.INFO, filename='test.log')


class BasePage(object):

    def __init__(self, driver):
        self.driver = driver

    def page_source_matches(self, text):
        """Verifies, that text appears in page"""
        logging.debug(f'Testing match: {text} in page:')
        logging.debug(self.driver.page_source)
        return text in self.driver.page_source

    def click_home_button(self):
        home_button = self.driver.find_element(*CommonLocators.HOME_BUTTON)
        home_button.click()


class LoginPage(BasePage):

    def login(self, username, password):
        '''Performs whole login operation'''
        login_input = self.driver.find_element(*LoginPageLocators.USERNAME_INPUT)
        password_input = self.driver.find_element(*LoginPageLocators.PASSWORD_INPUT)
        login_button = self.driver.find_element(*LoginPageLocators.LOGIN_BUTTON)
        login_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()


class NoteForm(BasePage):

    def type_note_description(self, description):
        note_description_input = self.driver.find_element(*NoteFormLocators.NOTE_DESCRIPTION_INPUT)
        note_description_input.send_keys(description)

    def type_note_value(self, value):
        note_value_input = self.driver.find_element(*NoteFormLocators.NOTE_VALUE_INPUT)
        note_value_input.send_keys(value)

    def select_note_category(self):
        pass

    def click_save_note_button(self):
        save_note_button = self.driver.find_element(*NoteFormLocators.NOTE_SAVE_BUTTON)
        save_note_button.click()

    def is_default_category(self, category_name):
        '''Checks if default selected category in form has specific name'''
        category_select = self.driver.find_element(*NoteFormLocators.NOTE_CATEGORY_SELECT)
        return category_name in category_select.text


class NoteListPage(BasePage):

    def click_delete_note_button(self):
        '''Click delete note and wait untill the row disappears'''
        delete_note_button = self.driver.find_element(*NotesListPageLocators.DELETE_NOTE_BUTTON)
        delete_note_button.click()
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located(NotesListPageLocators.DELETE_NOTE_BUTTON))

    def click_modify_categories_link(self):
        '''Click link to open 'modify categories' page'''
        modify_categories_link = self.driver.find_element(*NotesListPageLocators.MODIFY_CATEGORIES_LINK)
        modify_categories_link.click()


class CategoryPage(BasePage):

    def type_category_name(self, name):
        category_name_input = self.driver.find_element(*CategoriesPageLocators.ADD_CATEGORY_INPUT)
        category_name_input.send_keys(name)

    def click_save_category_button(self):
        save_category_button = self.driver.find_element(*CategoriesPageLocators.SAVE_CATEGORY_BUTTON)
        save_category_button.click()

    def click_set_default_category_button(self):
        set_default_category_button = self.driver.find_element(*CategoriesPageLocators.SET_DEFAULT_CATEGORY_BUTTON)
        set_default_category_button.click()

    def click_delete_category_button(self):
        delete_note_button = self.driver.find_element(*CategoriesPageLocators.DELETE_CATEGORY_BUTTON)
        delete_note_button.click()
