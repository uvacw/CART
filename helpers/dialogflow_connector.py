import os, ast
from google.cloud import dialogflow
from google.oauth2.service_account import Credentials
import json, proto


def proto_message_to_dict(message: proto.Message) -> dict:
    """Helper method to parse protobuf message to dictionary."""
    return json.loads(message.__class__.to_json(message))


def detect_intent_texts(session_id, text):
       '''Connects to DialogFlow using the environment variables 'DF_LANGUAGE_CODE' to determine the language code, 'DF_CREDENTIALS' for authentication.
       Credentials need to be stored as an environment variable. Before doing so, line-breaks need to be removed, and double-quotes turned into single-quotes.
       '''

    try:
        language_code = os.environ['DF_LANGUAGE_CODE']

        credentials = os.environ['DF_CREDENTIALS']

        
        credentials = ast.literal_eval(credentials)

        project_id = credentials['project_id']

        cr = Credentials.from_service_account_info(credentials)
        session_client = dialogflow.SessionsClient(credentials=cr)

        session = session_client.session_path(project_id, session_id)
        print('Session path: {}\n'.format(session))

        text_input = dialogflow.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={'session': session, 'query_input': query_input})


        response = proto_message_to_dict(response.query_result)
    except Exception as e:
        response = 'DialogFlow error: ' + str(e) 

    return response

if __name__ == '__main__':
    bot_code = 'TEST2'
    session_id = '1223455'
    text = 'Hello'
    language_code = 'EN'
    print(detect_intent_texts(session_id, text, bot_code))



