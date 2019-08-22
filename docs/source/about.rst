..  _about:

About CART
========================================================================

Objectives
^^^^^^^^^^
The Conversational Agent Research Toolkit (CART) aims at enabling researchers to create conversational agents for experimental studies using computational methods. CART provides a unifying toolkit written in Python that integrates existing services and APIs for dialogue management, natural language understanding & generation, and frameworks that enable publishing the conversational agents as either a web interface or within messaging apps. Specifically developed for communication research, CART not only acts as an integration layer across these different services, but also aims to provides a configurable solution meeting the requirements of academic research.

Components
^^^^^^^^^^

CART acts as an integration layer between several services so it can generate a conversational agent that can interact with participants of an experiment, log the conversations, design experiments, and connect with questionnaires for self-reported measures. To do so, CART works with the following components:


Dialogue Management
###################

CART currently uses `DialogFlow <https://www.dialogflow.com>`_ as the primary tool to handle dialogue managemnt. This means that all the participant input, and the responses that the agent gives, are primarily setup in DialogFlow. Using specific tokens (see below), the researcher can customise the responses that the agent provides depending on the condition that the participant is in.


Agent Publication
#################

CART currently uses the `Microsoft Bot Framework <https://dev.botframework.com/>`_ to publish the conversational agent. Within CART, the Bot Framework is responsible for creating a webchat for users to chat with the agent. This webchat can be embedded in online surveys. The Bot Framework also allows the agent to be published in other channels (e.g., Skype, Telegram, Facebook Messenger) without needing to change the code within CART.


Conversation Logging
####################

One of the key aspects of CART is the ability to log the conversations that participants in an experiment have with the agent. To do so, CART connects to a database under the control of the researcher.


Experiment Design
#################

CART allows the researcher to create experiments in which the same agent acts in different ways depending on the condition that the participant is in. To do so, the researcher simply needs to add specific tokens in the Dialogue Management tool, and setup different conditions within CART itself.


Online Questionnaire Integration
################################

After an agent is created and published, the researcher can integrate it to the flow of an online questionnaire (e.g., Qualtrics, SurveyMonkey). By turning on the *questionnaire flow*, the agent requests a unique ID from the participant, and returns a unique conversation code at the end of the conversation, so the researcher can link the conversation logs in the CART database with the responses in the online questionnaire.