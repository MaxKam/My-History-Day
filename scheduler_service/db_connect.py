import sqlite3


class DBConnect(object):

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    
    def get_sms_users(self):
        self.c = self.conn.cursor()
        self.sms_users = []
        for row in self.c.execute('SELECT * FROM users WHERE sendSMS=True'):
            self.sms_users.append(row)
        self.c.close()
        return self.sms_users


    
