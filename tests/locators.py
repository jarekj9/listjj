#!/usr/bin/env python3

from selenium.webdriver.common.by import By
from constants import *


class CommonLocators(object):
    HOME_BUTTON = (By.XPATH, '//h1')


class LoginPageLocators(object):
    USERNAME_INPUT = (By.ID, 'id_username')
    PASSWORD_INPUT = (By.ID, 'id_password')
    LOGIN_BUTTON = (By.XPATH, '//button[contains(text(), "Login")]')


class NoteFormLocators(object):
    NOTE_DESCRIPTION_INPUT = (By.ID, 'id_description')
    NOTE_VALUE_INPUT = (By.ID, 'id_value')
    NOTE_CATEGORY_SELECT = (By.ID, 'id_category')
    NOTE_SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")


class NotesListPageLocators(object):
    DELETE_NOTE_BUTTON = (By.XPATH, f'//td[contains(text(), \
        "{C.NOTE_DESCRIPTION}")]/following::button[contains(text(), "Delete")]')
    MODIFY_CATEGORIES_LINK = (By.XPATH, '//a[contains(text(), "categories")]')
    EXPORT_LINK = (By.XPATH, '//a[contains(text(), "Export")]')


class CategoriesPageLocators(object):
    ADD_CATEGORY_INPUT = (By.ID, 'id_category')
    SAVE_CATEGORY_BUTTON = (By.XPATH, '//button[contains(text(), "Save")]')
    DELETE_CATEGORY_BUTTON = (By.XPATH, f'//td[contains(., \
        "{C.CATEGORY}")]/following::button[contains(text(), "Delete")]')
    EDIT_CATEGORY_BUTTON = (By.XPATH, f'//td[contains(text(), \
        "{C.CATEGORY}")]/following::a[contains(text(), "Edit")]')
    SET_DEFAULT_CATEGORY_BUTTON = (By.XPATH, f'//td[contains(text(), \
        "{C.CATEGORY}")]/following::button[contains(text(), "Default")]')
