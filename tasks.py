# IMPORTING CONFIGURATIONS
import yaml

try:
    with open('config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)
except:
    with open('../config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)



# IMPORTING NECESSARY PACKAGES
from microsoftbotframework import ReplyToActivity
from helpers.db_class import DB
import json
import os.path
import apiai
from numpy.random import randint
from datetime import datetime
from helpers.rephrase import check_rephrase, check_override
from helpers.log_conversations import log_response, log_message, get_conversation_status, get_participantid_invalid

db = DB()

## TO DO:
## Logging
## Check participant ID
## Create and/or update conversation
## Check conversation status
## Standard messages



def echo_response(message):
    conditionid = None
    participantid = None
    # CONTACT RELATION UPDATE: Agent is added to Skype
    if message["type"] == "contactRelationUpdate":
        if 'action' in message.keys():
            if message['action'] == 'add':
                resp_speech = '[STANDARDWELCOMEMESSAGE]'
                resp_speech = check_rephrase(resp_speech)

                log_response(db, message, resp_speech, resp_speech)
                if 'channelData' in message.keys():
                    del message['channelData']['clientActivityID']
                ReplyToActivity(fill=message,
                        text=resp_speech).send()
                return


    # MESSAGE: Default type of conversation  
    if message["type"] == "message":
        if 'text' not in message.keys():
            message['text'] = '-'

        message['text'] = str(message['text']).replace("'", '‘')
        conversationid = message['conversation']['id']
        conversationid_trunc = conversationid[0:35]

        
        resp_speech = None
        ai = apiai.ApiAI(cfg['other']['dialogflow_access_token'])
        request = ai.text_request()
        request.lang = 'en'  # optional, default value equal 'en'
        request.session_id = conversationid_trunc
        request.query = message['text']

        respAPI = request.getresponse()
        resp = respAPI.read().decode('utf-8')
        resp = json.loads(resp)
        
        
        if not resp_speech:
            try:
                resp_speech  = resp['result']['fulfillment']['speech'] 
            except:
                resp_speech = resp['result']['fulfillment']['messages'][0]['speech']



        conversation_status, conversation_code, conditionid, participantid  = get_conversation_status(db, conversationid, message, resp)
        print(conversation_code, conditionid, conversation_status)

        


        message = log_message(db, message, participantid=participantid)
        override = check_override(message['text'])


        ## Performing manual connection if intents in DialogFlow
        connect_intent = None
        # If the conversation_status is considered invalid (due to invalid participant id)
        if conversation_status == 'conditionid_invalid':
            override_invalid_participantid = get_participantid_invalid()
            if override_invalid_participantid:
                connect_intent = '[' + str(override_invalid_participantid) + ']'
                log_response(db, message, connect_intent, conversation_status, participantid = participantid)

        # If the response in DialogFlow needs to connect manually to a new intent
        elif 'connect_intents' in cfg.keys():
            for source_intent, target_intent in cfg['connect_intents'].items():
                if resp_speech == '[' + str(source_intent) + ']':
                    print('check 1:', source_intent)
                    connect_intent = '[' + str(target_intent) + ']'
                    log_response(db, message, connect_intent, conversation_status, participantid = participantid)

        if connect_intent:
            ai = apiai.ApiAI(cfg['other']['dialogflow_access_token'])
            request = ai.text_request()
            request.lang = 'en'  # optional, default value equal 'en'
            request.session_id = conversationid_trunc
            request.query = connect_intent

            respAPI = request.getresponse()
            resp = respAPI.read().decode('utf-8')
            resp = json.loads(resp)
            try:
                resp_speech  = resp['result']['fulfillment']['speech'] 
            except:
                resp_speech = resp['result']['fulfillment']['messages'][0]['speech']

            resp_speech = check_rephrase(resp_speech, conversation_code = conversation_code, conditionid=conditionid)
            log_response(db, message, resp_speech, resp, participantid=participantid)
            if 'channelData' in message.keys():
                del message['channelData']['clientActivityID']            
            ReplyToActivity(fill=message, text=resp_speech).send()




        
        elif override['override'] == True:
            resp_speech = check_rephrase(override['resp_speech'], conversation_code = conversation_code)
            reason_override = override['reason']
            log_response(db, message, resp_speech, reason_override, participantid=participantid)
            ReplyToActivity(fill=message,
                        text=resp_speech).send()


        else:
            resp_speech = check_rephrase(resp_speech, conversation_code = conversation_code, conditionid=conditionid)
            message['textFormat'] = 'markdown'
            log_response(db, message, resp_speech, resp, participantid=participantid)
            #override for disappearing messages
            if 'channelData' in message.keys():
                del message['channelData']['clientActivityID']
            ReplyToActivity(fill=message, text=resp_speech).send()