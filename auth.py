from db import DatabaseConnection
from hashlib import sha256


class AuthManager:
    queries = {
        "CREATE_PASSWORD_ENTRY": "INSERT INTO AUTH(USER_ID,PASSWORD) VALUES('{}','{}') ",
        "RETRIEVE_USER_HASH": "SELECT PASSWORD FROM AUTH WHERE USER_ID = '{}' "
    }

    def __init__(self, db=None):
        self.db = db or self.get_db_connection()

    def get_db_connection(self):
        db = DatabaseConnection('access_control.db')
        db.connect()
        return db

    def register(self, user_id, txt_password):
        current_password = sha256(txt_password.encode('ascii')).hexdigest()
        try:
            self.db.write(self.queries["CREATE_PASSWORD_ENTRY"].format(user_id, current_password))
        except Exception as e:
            print('Unable to register new user')
            print(e)
            return False
        return True

    def login(self, user_id, txt_password):
        # print('user id obtained', user_id)
        current_hash = sha256(txt_password.encode('ascii')).hexdigest()
        user_query_result = self.db.read(self.queries["RETRIEVE_USER_HASH"].format(user_id))
        try:
            row = user_query_result[1]
            # print(row)
            if not row:
                print("Account not found")
                return False
            fetched_hash = row[0][0]
            # print(current_hash)
            # print(fetched_hash)
            if fetched_hash == current_hash:
                # print("Login Success.")
                return True
            print("Login Fail.")
        except Exception as e:
            print("Could not log in due to database error")
            raise e
            return False
        return False

