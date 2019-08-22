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

def get_special_fields():
    special_functions = cfg['special_functions']
    special_fields_logs = {}
    special_fields_conversations = {}
    for spfunc in special_functions.values():
        if spfunc['store_output'] == 'logs':
            special_fields_logs[spfunc['store_output_field']] = spfunc['store_output_field_type']
        if spfunc['store_output'] == 'conversations':
            special_fields_conversations[spfunc['store_output_field']] = spfunc['store_output_field_type']

    return special_fields_logs, special_fields_conversations



def create_logs(cur):
    try:
        special_fields_logs, special_fields_conversations = get_special_fields()
    except:
        special_fields_logs = {}
        special_fields_conversations = {}    

    sql_start = '''CREATE TABLE `logs` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `timestamp` datetime,
      `event` text,
      `participantID` text,
      `text` text,
      `message` text,
      `userData` text,
      `conversationid` text,
      `conversationid_trunc` text,
      `response_diag` text,'''
    sql_end = '''  PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;'''

    if len(special_fields_logs.keys()) > 0:
        for field_name, field_type in special_fields_logs.items():
            sql_start += ' `'+field_name+'` '+str(field_type)+', '
    sql = sql_start + sql_end
    cur.execute(sql)


    print('check_db: creating table logs')

def create_conversations(cur):
    try:
        special_fields_logs, special_fields_conversations = get_special_fields()
    except:
        special_fields_logs = {}
        special_fields_conversations = {}
    
    sql_start = '''
    CREATE TABLE `conversations` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `conversationid` text,
      `conversationid_trunc` text,
      `conversation_code` text,
      `status` text,
      `turns` int(11) DEFAULT '0',
      `initial_message` text,
      `first_name` text,
      `participantid` text,
      `conditionid` text,'''

    sql_end = '''  PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
    '''
    if len(special_fields_conversations.keys()) > 0:
        for field_name, field_type in special_fields_conversations.items():
            sql_start += ' `'+field_name+'` '+str(field_type)+', '
    sql = sql_start + sql_end


    cur.execute(sql)

    print('check_db: creating table conversations')


def check_db():
    """Connects to the databse informed in the configuration file and checks whether all tables are created. If tables are missing, it creates the tables. Does not return any values."""
    conn = pymysql.connect(host=host, port=3306, user=user, passwd=pwd, db=dbname, charset = 'utf8mb4')
    cur = conn.cursor()

    # Checking whether tables are created
    cur.execute('SHOW TABLES')
    tables = cur.fetchall()
    if len(tables) == 0:
        try:
            create_logs(cur)
            conn.commit()
        except Exception as e:
            print(e)
        try:
            create_conversations(cur)
            conn.commit()
        except Exception as e:
            print(e)

        return

    else:
        cur.execute('SHOW TABLES')
        tables = cur.fetchall()
        tables = [item[0] for item in tables]
        print(tables)
        if 'logs' not in tables:
            create_logs(cur)
            conn.commit()
            cur.execute('SHOW TABLES')
            tables = cur.fetchall()
            tables = [item[0] for item in tables]
        if 'conversations' not in tables:
            create_conversations(cur)
            conn.commit()
        print('check_db: all tables required available')        
    return

