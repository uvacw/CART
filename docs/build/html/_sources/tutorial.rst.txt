..  _tutorial:

Tutorial
========================================================================

This tutorial shows how to create an agent for an experiment as discussed in [REFERENCE TO CCR PAPER].

Agent specifications:

* The agent is embedded in a survey flow, and is presented during the survey
* The agent validates a participant id (to start the conversation) and provides a conversation code (at the end of the conversation)
* The agent automatically assigns users to conditions - humanlike or machine - and interacts different with each participant depending on the condition
* A sentiment analysis tool (Vader) is applied to each utterance by the participant, and the results are stored in the logs table in the database



Installation
^^^^^^^^^^^^

The basic steps to set up an agent are explained in :ref:`installation-setup-guide`. After the basic setup is done, the agent should be up and running - i.e., providing responses - even if irrelevant - to inputs provided by the participant through the web chat (or other channels).

With the agent running, the researcher can then customize the agent for an experiment, as outlined in the following sections.


Configurations in the dialogue management tool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Four intents are created in DialogFlow:

* *Welcome*: starts when the participant greets the agent, asks for the participant id, and - if the participant id is valid - ends with a token (``[PARTICIPANTID_VALID]``) for CART to know that the next intent (*Experiment*) needs to be connected
* *Experiment*: starts when CART has received a token indicating that the participant id is valid (``[PARTICIPANTID_VALID]``) and has sent a start token (``[START_EXPERIMENT]``) to DialogFlow. It ends when all the questions in the experimental setup are asked to the participant, providing a conversation code and telling the participant to continue with the survey.
* *Invalid participant id*: intent that is triggered by CART when the participant id provided by the participant in the *Welcome* intent is not valid.
* *Validate participant id*: fallback intent, which provides instructions for the participant should she want to try to start over (and provide a new participant id).

A copy of the agent, including the full dialogue, is available in the folder [ANONYMIZED LINK TO THE TUTORIAL FOLDER ON GITHUB]


Configurations in CART:
^^^^^^^^^^^^^^^^^^^^^^^

The full ``config.yaml`` file (without the authentication credentials for the API services, which need to be filled out by each researcher) is also available at [ANONYMIZED LINK TO THE TUTORIAL FOLDER ON GITHUB]. The key configurations look as follows:


In the ``other`` section, the conversationcode_suffix and the conversationcode_base are added to ensure that participants receive a conversation code at the end of the conversation, and that it always starts with a B, and counting from number 1500 (to prevent low numbers):::

    other:
        conversationcode_suffix: B
        conversationcode_base: 1500


The ``experimental_design`` section indicates that CART will assign participants to conditions using the ``random_balanced`` option, and that there will be two conditions, one fr machine, and another for the humanlike agent.::

    experimental_design:
        assignment_manager: CART
        assignment_method: random_balanced
        conditions:
            condition_1:
                condition_name: machine
            condition_2:
                condition_name: humanlike


The ``rephrases`` section has the specific text that varies per condition. The tokens (e.g., AGENTNAME) are included as placeholders in the DialogFlow configurations, so that CART can substitute them depending on the condition the participant is in. ::

    rephrases:
        condition_1:
            AGENTNAME: NutriBot
            ACKNOWLEDGEMENT1: OK. The system needs some information about you before it can make a recommendation.
            ACKNOWLEDGEMENT2: OK.
            ACKNOWLEDGEMENT3: OK, and 
            RECOMMENDATION: OK. Based on the your answers, the recommended breakfast is
            CLOSURESTART: Thank you. 
            CLOSUREEND: Conversation ended.
        condition_2:
            AGENTNAME: Ben
            ACKNOWLEDGEMENT1: Great! Let's get started then. I need to know a bit more about you before I can make a suggestion.
            ACKNOWLEDGEMENT2: Gotcha!
            ACKNOWLEDGEMENT3: Cool! And, just between the two of us
            RECOMMENDATION: Thanks! Hey... so here's an idea for your breakfast...
            CLOSURESTART: OK! Thanks a million for chatting with me! 
            CLOSUREEND: Have a great day!


The ``connect_intents`` section is used to make the connection between the *Welcome* and *Experiment* intents in DialogFlow when the participant id is considered valid by CART. ::

    connect_intents:
            PARTICIPANTID_VALID: START_EXPERIMENT

The ``questionnaire_flow`` section is configured to ensure that it is enabled and specify that the conversation with the agent takes place during the survey. As the *Welcome* intent asks for the participant id, this section further specifies that the parameter *participantid* in DialogFlow's responses should be looked for and parsed to detect participant id's. Only id's starting with an A (and ending with a number) are accepted. Two tokens are defined to handle cases when the participant id is valid or invalid. ::


    questionnaire_flow:
        enabled: True
        moment: during
        config_during:
            participantid_dialog_field: participantid
            participantid_not_recognized: PARTICIPANTID_INVALID
            participantid_recognized: PARTICIPANTID_VALID
            participantid_valid_suffixes: A

Finally, as sentiment analysis will be applied, the ``special_functions`` section is added with the name of the function, where to store the results in the database (and the type of field). As no override is configured, the ``funcion_action`` is set to False. ::

    special_functions:
        function_1:
            function_name: check_sentiment
            store_output: logs
            store_output_field: sentiment
            store_output_field_type: float
            function_action: False


For the sentiment analysis to run, two additional files need to be edited. First, the ``requirements.txt`` is edited to include ``vaderSentiment`` as a required Python module to be installed. Second, the ``special_functions.py`` file (inside the helpers folder) is edited to include the function that processes the user_message: ::

    ## EXAMPLE - SENTIMENT ANALYSIS
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    def check_sentiment(user_message):
        try:
            sentiment = analyzer.polarity_scores(user_message)
            sentiment = sentiment['compound']
            return sentiment
        except:
            return None




