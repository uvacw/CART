# CART - Conversational Agent Research Toolkit

The Conversational Agent Research Toolkit (CART) is aimed at enabling researchers to create conversational agents for experimental studies using computational methods. CART provides a unifying toolkit written in Python that integrates existing services and APIs for dialogue management, natural language understanding & generation, and frameworks that enable publishing the conversational agents as either a web interface or within messaging apps.


## Requirements

CART is written in Python 3.8, and needs run in a server able to execute Python code (serving a Flask application with an https certificate) and host a MySQL database. The [documentation](https://cart.readthedocs.io/en/latest/) demonstrates how to use Heroku (for the web server) and a database service (e.g., AWS RDS).

CART requires also access to two API services:
* [DialogFlow](https://dialogflow.com), for dialogue management
* [Microsoft Bot Framework](https://dev.botframework.com/), to publish the agent online in a web chat or in other channels (e.g., Skype, Telegram, Facebook Messenger)

Note: CART has been updated in May 2021 to reflect the new way to connect with DialogFlow's API. The DialogFlow credentials need to be set as environment variables (e.g., config vars). More information is available in the [documentation](https://cart.readthedocs.io/en/latest/installation.html#installation-setup-guide) (see steps 3 and 5).


## Installing and Using CART

Documentation on how to install and use CART is available here: https://cart.readthedocs.io/en/latest/
