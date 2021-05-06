
..  _installation:

Installation
========================================================================

Requirements
^^^^^^^^^^^^

Services and APIs
#################

CART acts as an integration layer between different services (and APIs), and specific configurations within CART itself. To use it, you will need:

1. Access to a SQL database
2. Access to a web service to publish CART (using Python 3.X)
3. An account with `DialogFlow <https://www.dialogflow.com>`_
4. An account with the `Microsoft Bot Framework <https://dev.botframework.com/>`_
5. A copy of the CART code

Optionally, you also would need access to an online questionnaire tool (e.g., Qualtrics, SurveyMonkey) if you are integrating CART into a survey flow.

**Note:** For #1 and #2, you can use your own server (if available), or AWS RDS (database) and Heroku (web service) as demonstrated in the :ref:`installation-setup-guide`.


Python Packages
###############

CART uses a set of Python packages (e.g., PyMySQL, `microsoftbotframework <https://github.com/mbrown1508/microsoftbotframework>`_, google-cloud-dialogflow etc.). By downloading CART and running the step-by-step instructions in the installation guide (below), all the necessary packages will be installed on the server.


.. _installation-setup-guide:

Installation and Setup Guide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Important note:** these steps show how to install and setup an agent using *AWS RDS* (as a database server) and *Heroku* (as a web service) along with *DialogFlow* and the *MS Bot Framework*. Advanced users can replace *AWS RDS* and *Heroku* by their own servers.

Step 1. Download CART to your computer
######################################

	1. Access [ANONYMIZED LINK OF THE GITHUB REPOSITORY] and select ``clone or download`` and download CART as a zip file.
	2. Extract the zip file in a folder you want to store the agent


Step 2. Rename the config.yaml file
###################################

The ``config.yaml`` file, located at the folder ``cart``, will contain all the basic configurations needed to connect to the services (MS Bot Framework and the SQL database), including usernames and passwords. **Never make it publicly available**.

To create it, you need to:
	1. Copy (or rename) the file called ``config_example.yaml`` to ``config.yaml``
	2. In the steps 3, 4 and 6 (below), you will need to update this file with information coming from each service.



Step 3. Create an agent in DialogFlow
#####################################

	1. Log in to `DialogFlow <https://www.dialogflow.com>`_ and select ``Create Agent``. For CART, all tests have been done with the ES (simpler) version.
	2. Follow the `instructions <https://cloud.google.com/dialogflow/es/docs/quick/setup>`_ from DialogFlow to enable the API, create a service account, and download the service key account file in JSON format. You will use it on step 5, as part of the web service configuration.



Step 4. Create a database for logging
#####################################

CART requires the the URL (host) of a MySQL database, database name, and username and password to connect to and log the conversations between the agent and participants. The username provided needs to have all privileges (including CREATE) in the database. This information needs to be made included in the ``config.yaml`` file. 

If using AWS RDS, the following steps need to be followed:
	1. Log into your `AWS <https://aws.amazon.com>`_  account and select RDS 
	2. Create a database using MySQL, and make sure to include the username and the password also in the ``config.yaml`` file
	3. When asked for the database name, make sure to inform it, and also include it in the ``config.yaml`` file.
	4. Select the endpoint of the database (check the dabatase details page), and paste it in the ``database_url`` field of ``config.yaml``.
	5. After the database is launched, make sure to check the security group (see database details), and open the inbound port to the server that you will be using.


*Notes:*
	* Usually a micro or small instance in AWS is sufficient for testing purposes, and can later be upgraded to medium/large when the agent is live and handling several conversations at the same time (e.g., during an experiment)
	* For security reasons, it is recommended not to allow any IP to connect to your database. When using Heroku, see this list of `plugins <https://elements.heroku.com/addons/categories/network>`_ that can create a static IP for your app.
	* When running the agent in the server for the first time, it will automatically create two tables in the database:
		* ``logs``, which records every interaction between the agent and the participant
		* ``conversations``, which records each individual conversation (i.e., in general, each participant = one conversation) that is started with the agent. 


Step 5. Publish the agent as a web service
##########################################

After completing the steps above, it is time to publish the agent as a web service. This can be done using Heroku (as demonstrated below) or in any other server that supports Python and Flask applications. It is important to note that the server should also be able to serve pages in https.

If using Heroku:
	1. Log into your `Heroku <https://heroku.com>`_  account and create a new app
	2. Set the environment variables (called in Heroku "config vars") for DialogFlow. See note 2, below, for details.
	3. Select the deployment method
	4. Deploy the app
	5. After the build has been completed, select ``open app``
	6. Copy the URL of the app (it should start with the app-name, and end with ``herokuapp.com``) to use in the next step

**Note 1:** the URL of the app is needed so it can be registered in the MS Bot Framework (next step). The registration in the MS Bot Framework will also provide authentication credentials. These credentials will need to be added to the ``config.yaml`` file, and the agent will need to be published again in Heroku (as outlined in the next step).

**Note 2:** Open the service account file downloaded on step 3(above) locally in a text editor, remove all line breaks, and substitute the double quotes (") by single quotes ('). In the web service, add this as an environment variable called DF_CREDENTIALS. Create another environment variable called DF_LANGUAGE_CODE and set its value to the appropriate language (e.g., en).


Step 6. Connect the agent to the MS Bot Framework
#################################################

After a URL for the agent as a web service is available (e.g., for Heroku: ``https://NAMEOFTHEAPP.herokuapp.com/``), the agent can be registered in the MS Bot Framework. To do so:

	1. Log in your `Microsoft Bot Framework <https://dev.botframework.com/>`_ account, selecting ``My Bots``
	2. Select ``create a bot``. You will be redirected to Azure Bot Service
	3. Select ``Bot Channels Registration``
	4. Provide the information required 
	5. The messaging endpoint will be the URL of the Heroku app + ``api/messages`` - example: ``https://NAMEOFTHEAPP.herokuapp.com//api/messages``
	6. After the channel registration is deployed, select ``Go to resource`` (or simply open it in Azure)
	7. In the ``Settings``, go to the Microsoft App ID area
	8. Copy the Microsoft App ID and add it to the ``config.yaml`` file under ``app_client_id``
	9. Click on ``Manage`` for the Microsoft App ID
	10. In the new window, select ``Generate new password``. Copy this password and add it to the ``config.yaml`` file under ``app_client_secret``
	11. Click on ``save`` and close this window
	12. In the ``config.yaml`` file, add the name of the agent under ``agent_name``
	13. Go back to Heroku and re-deploy the app (with the latest version of the ``config.yaml`` file).
	14. After the redeployment, you can use ``Test in Web Chat`` function on Azure Bot Service (same area where the ``Settings`` were) to test the connection.	



Step 7. Customize the agent
###########################

After the agent is connected to the MS Bot Framework, the basic setup is done. The researcher can then use several features within CART to customize the agent. For more details, see :ref:`using` 


Step 8. Making the agent available
##################################

After the agent is ready to interact with users, you can use the `Microsoft Bot Framework <https://dev.botframework.com/>`_ to publish it as a Web Chat (see ``Get bot embed codes``), or on other channels such as Skype, Facebook Messenger, or Telegram.



















