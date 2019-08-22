from helpers.check_db import check_db
check_db()


from microsoftbotframework import MsBot
from tasks import *

import os

bot = MsBot()
bot.add_process(echo_response)
# bot.add_process(send_to_conversation)

if __name__ == '__main__':
    bot.run()