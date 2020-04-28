# IMPORTING CONFIGURATIONS
import yaml

try:
    with open('config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)
except:
    with open('../config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)



import datetime, random, re
try:
    from special_functions import *
except:
    from helpers.special_functions import *


def log_message(db, message, participantid = None):
    """Logger module for messages coming from the participant. \n
    Requires: \n
    - A db object (from db_class)\n
    - A message dictionary containing, at least:\n
    -- ['text'] - text of the message\n
    -- ['conversation']['id'] - with the id of the conversation\n
    -- ['from']['name'] - with the name (or anonymised name) of the participant\n
    - Optionally: the participantID\n
    
     """
    conversationid = message['conversation']['id']
    conversationid_trunc = conversationid[0:35]
    now = datetime.datetime.now()

    sql = "INSERT INTO logs(event, text, message, userData, conversationid, conversationid_trunc, participantid, timestamp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    if 'name' in message['from'].keys():
        cur = db.query(sql, attributes=( "user", str(message['text']), str(message), str(message['from']['name']), conversationid, conversationid_trunc, participantid, now))
    else:
        cur = db.query(sql, attributes=( "user", str(message['text']), str(message), str(message['from']), conversationid, conversationid_trunc, participantid, now))

    db.commit()

    try:
        cfg_special_functions = cfg['special_functions'].values()
    except:
        cfg_special_functions = []
    
    functions_to_run = {}
    for item in cfg_special_functions:
        if item['store_output'] == 'logs':
            result_function = eval(item['function_name'])(str(message['text']))
            field = item['store_output_field']
            sql = 'UPDATE logs SET ' + field + ' = %s WHERE conversationid = %s AND text = %s'
            cur = db.query(sql, attributes = (result_function, conversationid, str(message['text'])))
            if item['function_action'] == True:
                function_comparison = item['function_comparison']
                if eval(str(result_function) + function_comparison):
                    message['text_old'] = message['text']
                    message['text'] = item['function_comparison_met']
                    return message

    return message


def log_response(db, message, resp_speech, resp, participantid = None):
    """Logger module for messages coming from the agent. \n
    Requires:\n
    - A db object (from db_class)\n
    - A message dictionary containing, at least:\n
    -- ['text'] - text of the message\n
    -- ['conversation']['id'] - with the id of the conversation\n
    -- ['from']['name'] - with the name (or anonymised name) of the participant\n
    - Optionally: the participantID\n
    - The text of the message (response of the agent)\n
    - The message object sent to the publishing platform\n
    - The response sent by the NLU/dialogue management module \n
     """
    conversationid = message['conversation']['id']
    conversationid_trunc = conversationid[0:35]
    now = datetime.datetime.now()

    sql = "INSERT INTO logs(event, text, response_diag, message, userData, conversationid, conversationid_trunc, participantid, timestamp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"


    if 'name' in message['from'].keys():
        cur = db.query(sql, attributes=("bot", resp_speech, str(resp), str(message), str(message['from']['name']),conversationid, conversationid_trunc, participantid, now))
    else:
        cur = db.query(sql, attributes=("bot", resp_speech, str(resp), str(message), str(message['from']),conversationid, conversationid_trunc, participantid, now))


    db.commit()

    return


def validate_participantid(participantid, participantid_valid_suffixes, resp, conditionid=None):
    """Module to validate participantid provided by the dialogue manager. Receives the participantid, the participantid_valid_suffixes (from the ``config.yaml`` file) and returns:\n
    * The cleaned-up participant id
    * If applicable, the conditionid (if assignment_manager is survey)
    * The conditionid_status (validated or conditionid_invalid) to determine if the participantid was validated or not.
    """
    participantid = str(participantid)
    conditionid_status = 'not_validated'

    assignment_manager = cfg['experimental_design']['assignment_manager']

    condition_names = {}
    conditions = cfg['experimental_design']['conditions']
    # print('validate_participantid conditions:', conditions)
    # print('participantid_valid_suffixes:', participantid_valid_suffixes)

    if assignment_manager.lower() == 'survey':
        for condition in conditions.values():
            condition_names[condition['condition_suffix']] = condition['condition_name']


    # Checking every token within what the respondent provided as participant id
    participantid = re.sub('[^A-Za-z0-9]+', ' ', participantid)
    participantid_tokens = participantid.split(' ')

    # print('validate_participantid tokens:', participantid_tokens)
    # print('condition_names:', condition_names)
    for token in participantid_tokens:
        for suffix in participantid_valid_suffixes:
            if suffix in token:
                try:
                    int(token.replace(suffix,''))
                    if assignment_manager.lower() == 'survey':
                        conditionid = condition_names[suffix]
                    conditionid_status = 'validated'
                    participantid = token
                    return participantid, conditionid, conditionid_status
                except:
                    conditionid_status = 'conditionid_invalid'

    conditionid_status = 'conditionid_invalid'   

    return participantid, conditionid, conditionid_status



def check_participantid(resp, status, conditionid = None):
    """Module to start the validation of the participant id if the questionnaire_flow == during or after, and if the response by the dialogue manager contains the key parameters, and inside parameters, the key that in ``config.yaml`` was assigned as participantid_dialog_field. """

    questionnaire_flow = cfg['questionnaire_flow']
    if questionnaire_flow['enabled'] == False:
        return conditionid, None, status

    if questionnaire_flow['moment'] == 'before':
        return conditionid, None, status

    if questionnaire_flow['moment'] == 'during':
        participantid_dialog_field = questionnaire_flow['config_during']['participantid_dialog_field']
        participantid_valid_suffixes = questionnaire_flow['config_during']['participantid_valid_suffixes']
        participantid_valid_suffixes = [item.strip() for item in participantid_valid_suffixes.split(',')]

    if questionnaire_flow['moment'] == 'after':
        participantid_dialog_field = questionnaire_flow['config_after']['participantid_dialog_field']
        participantid_valid_suffixes = questionnaire_flow['config_after']['participantid_valid_suffixes']
        participantid_valid_suffixes = [item.strip() for item in participantid_valid_suffixes.split(',')]

    if type(resp) == dict:
        if 'result' in resp.keys():
            if 'parameters' in resp['result'].keys():
                if participantid_dialog_field in resp['result']['parameters']:
                    participantid = resp['result']['parameters'][participantid_dialog_field]
                    # print('participantID_in_check_participantid', participantid)
                    if len(participantid) > 0:
                        participantid, conditionid, conditionid_status = validate_participantid(participantid, participantid_valid_suffixes, resp, conditionid = conditionid)
                        if conditionid_status == 'conditionid_invalid':
                            print(conditionid_status)
                            status = conditionid_status
                            participantid = None
                        # print('return of check_participant_id():', conditionid, participantid, status)
                        return conditionid, participantid, status


    return conditionid, None, status


def get_participantid_invalid():
    questionnaire_flow = cfg['questionnaire_flow']
    if questionnaire_flow['enabled'] == False:
        return None

    if questionnaire_flow['moment'] == 'before':
        return None

    if questionnaire_flow['moment'] == 'during':
        return questionnaire_flow['config_during']['participantid_not_recognized']

    if questionnaire_flow['moment'] == 'after':
        return questionnaire_flow['config_after']['participantid_not_recognized']

    return None




def get_first_name(message):
    """Function tries to retrieve the first name of the user depending on the message provided by the MS Bot Framework. If it finds a name, it returns the first token. If not, returns an empty string. """
    try:
        if message['channelId'] == 'skype':
            name = message['from']['name'].split(' ')[0]
        elif message['channelId'] == 'telegram':
            name = message['channelData']['message']['from']['first_name']
        else:
            name = ''
    except:
        name = ''

    return name


def assign_conditions(db):
    """Assigns the condition to a new conversation based on the configurations available at the ``config.yaml`` file (section: experimental_design).\n\n
    If the ``assignment_manager`` is set to ``CART``, it works as follows:\n
    1. It uses the conditions available at the ``config.yaml`` file to determine the conditions for the experiment, and uses the condition_name as the value to be informed.
    2. It assigns the condition to the new conversation depending on the ``assignment_method`` in the ``config.yaml`` file:\n
    - If the ``assignment_method`` is set to ``fully_random``, it will randomly choose among the conditions.\n
    - If the ``assignment_method` is set to ``random_balanced``, it will return the condition with the lowest count in the database and, if all conditions are equally balanaced, will return a random choice among the conditions.\n
    - If the ``assignment_method` is set to ``sequential``, it will return the next condition (as per the order in the config file) compared to the last conversation available in the database.\n
    """
    experimental_design = cfg['experimental_design']
    if experimental_design['assignment_manager'] == 'CART':
        conditions = []
        for condition in experimental_design['conditions'].values():
            conditions.append(condition['condition_name'])

        if experimental_design['assignment_method'] == 'fully_random':
            return random.choice(conditions)

        if experimental_design['assignment_method'] == 'random_balanced':
            from collections import Counter
            sql = 'SELECT conditionid FROM conversations'
            db.commit()
            cur = db.query(sql)
            results = cur.fetchall()
            if len(results) == 0:
                return random.choice(conditions)

            results = [item[0] for item in results]

            counts = Counter(results).values()
            if len(set(counts))==1:
                condition_present = Counter(results).most_common()[0]
                potential_conditions = [item for item in conditions if item != condition_present]
                if len(potential_conditions) > 0:
                    return random.choice(potential_conditions)
                else:
                    return random.choice(conditions)
            else:
                least_frequent_condition = Counter(results).most_common()[-1][0]
                return least_frequent_condition

        if experimental_design['assignment_method'] == 'sequential':
            sql = 'SELECT conditionid FROM conversations'
            db.commit()
            cur = db.query(sql)
            results = cur.fetchall()
            if len(results) == 0:
                return conditions[0]

            results = [item[0] for item in results]
            last_cond = results[-1]

            total_cond = len(conditions)
            if conditions.index(last_cond) + 1 == total_cond:
                return conditions[0]
            else:
                return conditions[conditions.index(last_cond) + 1]

        else:
            return random.choice(conditions)

    return 

def get_conversation_status(db, conversationid, message, resp, participantid=None):
    """Receives the conversationid and the message from the user, and uses this information to determine the conversation status.\n\n
    If the conversationid is found in the database (table conversations), the function increases the number of turns by 1, and returns the status, conversation_code and the conditionid.\n\n
    If the conversationid is not found, it will create a new row in the table conversations, and include:\n
    - conversation_code: created using the ``conversationcode_suffix`` + the ``conversationcode_base`` (number) from the ``config.yaml`` file, incremented by the number of conversations already in the database.\n
    - conditionid: created using the assign_conditions function
    - status: 0 (for conversation that has started)
    - turns: 1
    
    \n\nThe function also calls ``assign_conditions()`` to assign conditions (when CART is set as the assignment manager in ``config.yaml``), and ``check_participantid()`` to determine if the integration with the survey requires checking the participant id.
    
    """

    conversationid_trunc = conversationid[0:35]
    sql = 'SELECT status, conversation_code, conditionid, id, participantid FROM conversations WHERE conversationid = %s'
    cur = db.query(sql, attributes=(conversationid))
    results = cur.fetchall()

    assignment_manager = cfg['experimental_design']['assignment_manager']

    if len(results) == 0:
        sql = 'SELECT MAX(id) FROM conversations'
        cur = db.query(sql)
        results = cur.fetchall()
        if len(results) == 0:
            max_id = 0
        else:
            max_id = results[0][0]
        if max_id == None:
            max_id = 0
        status = 0


        first_name = get_first_name(message)
        conversation_code = str(cfg['other']['conversationcode_suffix']) + str(cfg['other']['conversationcode_base'] + int(max_id))

        if assignment_manager == 'CART':
            conditionid = assign_conditions(db)

        else:
            conditionid = None

        sql = 'INSERT INTO conversations(conversationid, conversationid_trunc, conversation_code, status, turns, initial_message, first_name, conditionid) VALUES (%s, %s, %s, %s, 1, %s, %s, %s)'  
        db.query(sql, attributes=(conversationid, conversationid_trunc, conversation_code, status, str(message), first_name, conditionid))
        db.commit()


    else:
        status = results[0][0]
        conversation_code = results[0][1]
        conditionid = results[0][2]
        participantid = results[0][4]

        if conditionid == None:
            conditionid, participantid, status = check_participantid(resp, status)
            if conditionid:
                sql = 'UPDATE conversations SET conditionid = %s, participantid = %s WHERE conversationid = %s'
                cur = db.query(sql, attributes=(conditionid, participantid, conversationid))
                db.commit()

        if participantid == None:
            conditionid, participantid, status = check_participantid(resp, status, conditionid = conditionid)
            if participantid:
                sql = 'UPDATE conversations SET participantid = %s WHERE conversationid = %s'
                cur = db.query(sql, attributes=(participantid, conversationid))
                db.commit()






        sql = 'UPDATE conversations SET turns = turns + 1 WHERE conversationid = %s'
        cur = db.query(sql, attributes=(conversationid))
        db.commit()
    return status, conversation_code, conditionid, participantid









if __name__ ==  "__main__":
    from db_class import DB
    db = DB()
    counter = 0
    while counter < 5:
        conversationid = 'TEST5' + str(counter)
        message = {'from': {'name': 'test_participant'}, 'text': 'test_resp_speech', 'conversation': {'id': 'test_ID'}}
        get_conversation_status(db, conversationid, message)
        counter += 1
    
