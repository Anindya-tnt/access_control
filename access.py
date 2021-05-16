"""
Command based interactive access control app

Usage:
    access.py [--debug-flag=<bool>]

Options:
    [--debug-flag=<bool>]             Set this to true to turn on debugging
"""
import hashlib, binascii
import os

import time
from docopt import docopt
from db import DatabaseConnection
from user import User
import logging

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(lineno)d] - %(message)s', level=logging.INFO)
logger = logging.getLogger('access')
args = docopt(__doc__)
debug_flag = args.get('--debug-flag') or False


def debug_log(statement, *args):
    if debug_flag:
        logger.info(statement.format(*args))


class AccessRequests:
    statements = {
        "ADMIN_WELCOME_MSG": "hi! you are logged in as admin",
        "LOGIN_USER": "press 1 for login as another user",
        "CREATE_USER": "press 2 for create user",
        "EDIT_ROLE": "press 3 for edit role",
        "VIEW_ROLE": "press 2 for view roles",
        "ACCESS_RESOURCE": "press 3 for access resource",
        "USER_WELCOME_MSG": "hi! you are logged in as {}",
        "QUIT_CONSOLE": "Press anything else to quit!",
        "AFTER_QUIT_MESSAGE": "Thank you! Hope to see you again."
    }

    def __init__(self, *args, **kwargs):
        self.db = DatabaseConnection('access_control.db')
        self.db.connect()
        self.current_user = User('admin', '', 'admin@accesscontrol.com', db=self.db)
        self.fetch_current_user_role()
        self.role_map = {0: 'RWD',
                         1: 'R',
                         2: 'W',
                         3: 'D',
                         4: 'RW',
                         5: 'RD',
                         6: 'WD'}

    def get_current_logged_in_user(self):
        return self.current_user

    def fetch_current_user_role(self):
        return self.current_user.fetch_role()

    def set_user_role(self):
        users = User.get_all_user_details(self.db)
        user_dict = dict()
        for index, user in enumerate(users):
            user_dict[index] = {'id': user[0], 'first_name': user[1], 'last_name': user[2], 'email': user[3]}
            print('Press {} for selecting user with email {}'.format(index, user[3]))
        user_index_id = int(input())
        selected_user = User(user_dict[user_index_id]['first_name'],
                             user_dict[user_index_id]['last_name'],
                             user_dict[user_index_id]['email'])
        print('Enter role choices from below list')
        for i in range(len(self.role_map)):
            print('Press {} for {} role'.format(i, self.role_map[i]))
        role = int(input())
        selected_user.set_role(self.role_map[role])
        print('Selected user\'s new role set to: {}'.format(selected_user.fetch_role()))

    def set_current_user(self, user_instance):
        self.current_user = user_instance

    def get_user_details_from_db(self):
        email_id = input('Enter your email_id: ')
        user_details = User.retrieve_details(self.db, email_id)
        # print(user_details)
        if user_details:
            return User(user_details[1],user_details[2],user_details[3])
        return None

    def get_user_details(self):
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        email = input('Enter email: ')
        return User(first_name, last_name, email)

    def create_user(self):
        self.get_user_details().register_new_user()

    def login_user(self):
        user_instance = self.get_user_details_from_db()
        current_logged_in_user = self.get_current_logged_in_user()
        if user_instance.email == current_logged_in_user.email:
            print('User is already logged in')
            return False
        if user_instance:
            is_logged_in = user_instance.login()
            if is_logged_in:
                self.set_current_user(user_instance)
                return is_logged_in
        print('Unable to login user')
        return False

    def process_choice(self, choice):
        current_role = self.current_user.fetch_role()
        is_admin = self.current_user.email == 'admin@accesscontrol.com'
        try:
            int_choice = int(choice)
        except (ValueError, TypeError) as e:
            debug_log('Could not process illegal choice')
            return False
        if int_choice == 1:
            self.login_user()
        elif int_choice == 2:
            self.create_user() if is_admin else print('Available roles are', User.get_all_role_details(self.db))
        elif int_choice == 3:
            if is_admin:
                self.set_user_role()
            else:
                resource_name = input('Enter resource name to access: ')
                valid_access_types = ['READ', 'WRITE', 'DELETE']
                print('Available access_types to choose are', valid_access_types)
                access_type = input('Enter access type: ')
                if access_type not in valid_access_types:
                    print('Not a valid choice .. returning to main menu')
                    return True
                granted = self.current_user.access_resource(resource_name, access_type)
        else:
            debug_log('Could not process illegal choice')
            return False
        return True

    def run(self):
        while True:
            print("*" * 50)
            if self.current_user.email == "admin@accesscontrol.com":
                print(self.statements["ADMIN_WELCOME_MSG"])
                print(self.statements["LOGIN_USER"])
                print(self.statements["CREATE_USER"])
                print(self.statements["EDIT_ROLE"])
            else:
                print(self.statements["USER_WELCOME_MSG"].format(self.current_user.first_name))
                print(self.statements["LOGIN_USER"])
                print(self.statements["VIEW_ROLE"])
                print(self.statements["ACCESS_RESOURCE"])
            print(self.statements["QUIT_CONSOLE"])
            debug_log('Current user email is {}'.format(self.current_user.email))
            debug_log('Current user role is {}'.format(self.current_user.fetch_role()))
            choice = input('Enter your choice: ')
            to_continue = self.process_choice(choice)
            if not to_continue:
                print(self.statements["AFTER_QUIT_MESSAGE"])
                break
            # time.sleep(1)
        print("*" * 50)
def main():
    # db = DatabaseConnection('access_control.db')
    # db.connect()
    # rows = db.read("SELECT * FROM USER")
    # print(rows)
    access_requests = AccessRequests(args)
    access_requests.run()


if __name__ == '__main__':
    main()