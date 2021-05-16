import os
import sqlite3


class DatabaseConnection:
    def __init__(self, database_path):
        self.database_path = database_path
        self._dbconn = None
        assert os.path.exists(self.database_path)

    def connect(self):
        try:
            self._dbconn = sqlite3.connect(self.database_path)
            return True
        except sqlite3.Error as e:
            print(e)
        except AssertionError as e:
            print('ERROR: database file not found.')
        return False

    def disconnect(self):
        if self._dbconn:
            self._dbconn.close()
            self._dbconn = None
            return True
        return False

    def get_cursor(self):
        if self._dbconn:
            c = self._dbconn.cursor()
            return c
        return False

    def write(self, query, *args, num_statements=1):
        try:
            assert any(map(lambda s: query.upper().strip().startswith(s),
                           ('CREATE TABLE', 'ALTER TABLE', 'INSERT', 'UPDATE', 'DELETE')))
            assert query.count('?') == len(args)
            c = self._dbconn.cursor()
            if num_statements == 1:
                c.execute(query, args)
            else:
                query_string = query.format(*args)
                # print(query_string)
                c.executescript(query_string)
            self._dbconn.commit()
            return 0
        except AssertionError:
            print('ERROR: inconsistent query arguments.')
        except sqlite3.Error as e:
            self._dbconn.rollback()
            print('SQL ERROR:', e)
        return -1

    def read(self, query, *args):
        try:
            assert query.count('?') == len(args)
            assert query.upper().strip().startswith('SELECT')
            c = self._dbconn.cursor()
            c.execute(query, args)
            rows = c.fetchall()
            return 0, rows;
        except AssertionError:
            print('ERROR: inconsistent query arguments.')
        except sqlite3.Error as e:
            print('SQL ERROR:', e)
        return -1, ()
