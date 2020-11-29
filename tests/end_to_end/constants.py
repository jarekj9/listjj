#!/usr/bin/env python3

import configparser

config = configparser.ConfigParser()
config.read('config.conf')


class C:
    HEADLESS = 1
    URL = config['test_config']['url']
    LOGIN_URL = URL + '/accounts/login'
    USERNAME = config['test_config']['username']
    PASSWORD = config['test_config']['password']
    DRIVER_PATH = config['test_config']['driver_path']
    NOTE_DESCRIPTION = 'test_note_jj'
    EDITED_NOTE_DESCRIPTION = 'test_note_jj_edited'
    NOTE_VALUE = '10'
    CATEGORY = 'test_category'
    EDITED_CATEGORY = 'test_category_edited'
