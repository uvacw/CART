# IMPORTING CONFIGURATIONS
import yaml

try:
    with open('config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)
except:
    with open('../config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)


from difflib import SequenceMatcher
import re


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def check_rephrase(resp_speech, conversation_code=None, conditionid=None):
    """Receives a potential response by the agent and checks if it needs rephrasing. If required, replaces any text within square brackets by appropriate information depending on conditions specified in this function. Returns the agent response with the information required replace.\n\nThe ``config.yaml`` file manages these replacements (section: ``rephrases``).\n\n
    
    Some specific operations:\n
    - If ``conversation_code`` is provided, the function will also look for the string ``|CONVERSATIONCODE|`` in the response, and substitute it by the value of the conversation_code. \n
        - This can be helpful for when the agent needs to provide a conversation_code to the user. For example, a message can be configured in the dialogue manager to say "This is your ``|CONVERSATIONCODE|``", and the check_rephrase function will automatically replace that piece of the string by the actual conversation code.\n
    - If ``conditionid`` is not specified, the function will only look for items to rephrase in the ``all_conditions`` section of the ``config.yaml`` file.\n
    - If a ``conditionid`` is specified, the function will look also for items to rephrase in each of the conditions. \n
        - For example, if condition_1 indicates that TEXT1 should be replaced by A, and condition_2 indicates that TEXT1 should be replaced B, the check_rephrase function will provide rephrase the response "This is TEXT1" differently depending on the condition.\n
        
        
     """
    # print(resp_speech, conversation_code)
    
    if conversation_code:
        resp_speech = resp_speech.replace('|CONVERSATIONCODE|', conversation_code)
    
    
    if '[' not in resp_speech:
        return resp_speech


    # REPHRASING
    if 'all_conditions' in cfg['rephrases'].keys():
        rephrases = cfg['rephrases']['all_conditions']
        for source, target in rephrases.items():
            resp_speech = resp_speech.replace('['+source+']', target)

    if conditionid:
        conditions = cfg['experimental_design']['conditions']
        condition_names = {}
        for key, value in conditions.items():
            condition_names[value['condition_name']] = key

        rephrases = cfg['rephrases'][condition_names[conditionid]]
        for source, target in rephrases.items():
            resp_speech = resp_speech.replace('['+source+']', target)

    # SURVEY INTEGRATION
    questionnaire_flow = cfg['questionnaire_flow']
    if questionnaire_flow['enabled'] == True:
        if questionnaire_flow['moment'] == 'before':
            if resp_speech == '['+str(questionnaire_flow['config_before']['rephrase_token']) + ']':
                resp_speech = questionnaire_flow['config_before']['rephrase_text'].replace('|CONVERSATIONCODE|', conversation_code)

        if questionnaire_flow['moment'] == 'during':
            if 'rephrase_end_token' in questionnaire_flow['config_during'].keys():
                if resp_speech == '['+str(questionnaire_flow['config_during']['rephrase_end_token']) + ']':
                    resp_speech = questionnaire_flow['config_during']['rephrase_end_text'].replace('|CONVERSATIONCODE|', conversation_code)

    if conversation_code:
        resp_speech = resp_speech.replace('|CONVERSATIONCODE|', conversation_code)



    return resp_speech

def check_override(user_message):
    """Checks if a message by a user requires any type of override - i.e., stopping the message from going to DialogFlow to get a response. \n\n
    
    To do so, it uses the information available in the ``overrides`` section of the ``config.yaml`` file. More specifically, it checks if any of the terms contained in the ``override_terms_in_user_message`` is present in the user_message, with the following rules:\n
    - If ``override_terms_case_sensitive`` is set to ``False``, it turns the user_message to lower case before continuing. If not, case is preserved.\n
    - If ``override_terms_matching`` is set to ``full_string``, it checks the user_message is equal to any of the terms in ``override_terms_in_user_message``. For example, if the user_message is "apple" and this is one of the terms, then it will meet the condition. If the user_message is "I like apple", it won't match.\n
    - If ``override_terms_matching`` is set to ``string``, it checks if each of the terms in ``override_terms_in_user_message`` is present in the user_message using string matching. For example, the term "apple" would be found in the messages "I like apple" and "I like pineapples".\n
    - If ``override_terms_matching`` is set to ``tokens``, it first splits the user_message in tokens (removing any punctuation marks or special characters), and then checks if any of the tokens of the user_message is present in the terms from ``override_terms_in_user_message``. For example, the term "apple" would be found in the messages "I like apple" but not in "I like pineapples".\n\n
    
    After completing the checks above, if any of the terms is found in the user_message, the function returns a dictionary containing:\n
    - resp_speech: the text that needs to be provided to the user.\n
    - override_reason:  the reason for the override\n
    - override: True\n\n
    
    If none of the terms is found, the function returns a dictionary only containing the key override with the value False.\n\n
    
    """
    
    result = {}
    result['override'] = False

    if 'overrides' in cfg.keys():

        overrides = cfg['overrides']

        for override in overrides.values():
            if override['override_terms_case_sensitive'] == False:
                user_message = user_message.lower()

            override_terms_in_user_message = override['override_terms_in_user_message'].split(',')
            override_terms_in_user_message = [str(term).strip() for term in override_terms_in_user_message]
            if override['override_terms_matching'] == 'full_string':
                for term in override_terms_in_user_message:
                    if user_message == term:
                        result['override'] = True
                        result['reason'] = 'override: ' + str(override['override_reason'])
                        result['resp_speech'] = override['override_response_from_agent']
                        return result
            if override['override_terms_matching'] == 'string':
                for term in override_terms_in_user_message:
                    if term in user_message:
                        result['override'] = True
                        result['reason'] = 'override: ' + str(override['override_reason'])
                        result['resp_speech'] = override['override_response_from_agent']
                        return result

            if override['override_terms_matching'] == 'tokens':
                user_message = re.sub('[^A-Za-z0-9]+', ' ', user_message)
                user_message = user_message.split(' ')
                for token in user_message:
                    if token in override_terms_in_user_message:
                        result['override'] = True
                        result['reason'] = 'override: ' + str(override['override_reason'])
                        result['resp_speech'] = override['override_response_from_agent']
                        return result


    return result