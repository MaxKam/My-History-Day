from sqlalchemy import create_engine
import psycopg2


class DBConnect(object):

    def __init__(self, db_user, db_password, db_host, db_port, db_name):
        self.engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(\
            db_user, db_password, db_host, db_port, db_name))

    
    def get_sms_users(self):
        self.sms_users = []
        for row in self.engine.execute("select * from users;"):
            self.sms_users.append(row)
        return self.sms_users


    
