import yaml

try:
    with open('config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)
except:
    with open('../config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)


host = cfg['other']['database_url']
user = cfg['other']['database_username']
pwd = cfg['other']['database_password']
dbname = cfg['other']['database_name']


import pymysql

class DB:
    conn = None

    def connect(self):
        self.conn = pymysql.connect(host=host, port=3306, user=user, passwd=pwd, db=dbname, charset = 'utf8mb4')

    def query(self, sql, attributes=None):
        try:
            cursor = self.conn.cursor()
            if attributes:
                cursor.execute(sql, attributes)
            else:
                cursor.execute(sql)
        except (AttributeError, pymysql.err.OperationalError):
            self.connect()
            cursor = self.conn.cursor()
            if attributes:
                cursor.execute(sql, attributes)
            else:
                cursor.execute(sql)
        return cursor

    def commit(self):
        try:
            self.conn.commit()
        except (AttributeError, pymysql.err.OperationalError):
            self.connect()
            self.conn.commit()
