from auth import AuthManager
from db import DatabaseConnection
from getpass import getpass


def debug_log(statement, debug_flag=False, *args):
    if debug_flag:
        logger.info(statement.format(*args))


class User:
    authenticated_users = set()
    queries = {
        "CHECK_USER": "SELECT ID, FIRST_NAME, LAST_NAME, EMAIL FROM USER WHERE email = '{}'",
        "CREATE_USER": "INSERT INTO USER(FIRST_NAME,LAST_NAME,EMAIL) VALUES('{}','{}','{}')",
        "GET_SALT": "SELECT SALT FROM AUTH WHERE USER_ID = '{}'",
        "GET_USER_ROLE": "SELECT R.NAME "
                         "FROM USER_ROLE UR "
                         "JOIN USER U ON U.ID = UR.USER_ID "
                         "JOIN ROLE R ON R.ID = UR.ROLE_ID "
                         "WHERE U.EMAIL = '{}' ",
        "SET_USER_ROLE": "UPDATE USER_ROLE SET ROLE_ID = (SELECT ID FROM ROLE WHERE NAME = '{}' ) "
                         "WHERE USER_ID = (SELECT ID FROM USER WHERE EMAIL = '{}'); "
                         "INSERT OR IGNORE INTO USER_ROLE (ROLE_ID, USER_ID) "
                         "VALUES ((SELECT ID FROM ROLE WHERE NAME = '{}') , (SELECT ID FROM USER WHERE EMAIL = '{}') )  ",
        "GET_ALL_USERS": "SELECT ID, FIRST_NAME, LAST_NAME, EMAIL FROM USER",
        "VIEW_ALL_ROLES": "SELECT NAME FROM ROLE",
    }

    @classmethod
    def get_authenticated_users(cls):
        logger.info('Authenticated users are {}'.format(cls.authenticated_users))
        return cls.authenticated_users

    @classmethod
    def get_all_role_details(cls, db):
        query_result = db.read(User.queries["VIEW_ALL_ROLES"])
        if not query_result[1]:
            print('No existing roles found')
            return False
        role_details = []
        for query_result_item in query_result[1]:
            role_details.append(query_result_item[0])
        return role_details

    @classmethod
    def get_all_user_details(cls, db):
        query_result = db.read(User.queries["GET_ALL_USERS"])
        if not query_result[1]:
            print('No existing users found')
            return False
        user_details = query_result[1]
        return user_details

    def __init__(self, first_name, last_name, email, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = None
        self.role = None
        self.auth_manager = self.get_auth_manager()

    def access_resource(self, resource_name, access_type):
        access_type_map = {'READ': 'R', 'WRITE': 'W', 'DELETE': 'D'}
        role = self.fetch_role()
        if not role:
            logger.info('Role not set yet')
            return False
        match = False
        if access_type_map[access_type] in role:
            match = True
        if not match:
            logger.info('Your role does not permit you {} access to resource {}'.format(access_type, resource_name))
        else:
            print('You are allowed {} access to resource: {}'.format(access_type, resource_name))

    def get_auth_manager(self):
        if not hasattr(self, 'db'):
            self.connect_db()
        return AuthManager(db=self.db)

    def is_authenticated(self):
        auth_users = self.get_authenticated_users()
        if self.id and self.id in auth_users:
            return True
        return False

    def connect_db(self):
        if hasattr(self, 'db'):
            return self.db
        db = DatabaseConnection('access_control.db')
        db.connect()
        self.db = db

    @classmethod
    def retrieve_details(cls, db, email):
        query_result = db.read(User.queries["CHECK_USER"].format(email))
        if not query_result[1]:
            logger.info('No existing user with email={} found'.format(email))
            return False
        user_details = query_result[1][0]
        return user_details

    def login(self):
        is_logged_in = False
        self.connect_db()
        user_id = User.retrieve_details(self.db, self.email)[0]
        if not user_id:
            logger.info('User Id not found')
        else:
            password_input = getpass(prompt='Enter your password: ', stream=None)
            authenticate = self.auth_manager.login(user_id, password_input)
            if authenticate:
                self.id = user_id
                self.authenticated_users.add(self.id)
                is_logged_in = True
        return is_logged_in

    def set_role(self, role):
        try:
            self.db.write(self.queries["SET_USER_ROLE"].format(role, self.email, role, self.email), num_statements=2)
        except Exception as e:
            print('Unable to set role')
            print(e)
            return False
        return True

    def fetch_role(self):
        if hasattr(self, 'role') and self.role:
            return self.role
        query_result = self.db.read(self.queries["GET_USER_ROLE"].format(self.email))
        if not query_result[1]:
            print('No role obtained from db')
            return None
        self.role = query_result[1][0][0]
        return self.role

    def register_new_user(self):
        print('Checking for existing user {} {}'.format(self.first_name, self.last_name))
        self.connect_db()
        query_result = self.db.read(User.queries["CHECK_USER"].format(self.email))
        if not query_result[1]:
            print('No existing user with email={} found'.format(self.email))
            password_input = None
            for retry_count in range(3):
                password_input = getpass(prompt='Enter new password: ', stream=None)
                password_confirmation = getpass(prompt='Enter new password once more: ', stream=None)
                if password_confirmation != password_input:
                    print('Passwords enter do not match..try again!')
                    continue
                break
            if password_confirmation != password_input:
                print('Please try registering from the beginning')
                return False
            self.db.write(User.queries["CREATE_USER"].format(self.first_name, self.last_name, self.email))
            user_id = self.retrieve_details(self.db, self.email)[0]
            register = self.auth_manager.register(user_id, password_input)
            if register:
                print('New user created')
                return True
            print('Unable to create new user credentials')
        else:
            print('User with email already exists')
        return False

    def logout(self):
        self.authenticated_users.remove(self.id)
        self.id = None
        print('User logged out')



