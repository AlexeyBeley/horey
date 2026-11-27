"""
Kafka API

"""

from telegram.ext import Updater, CommandHandler, Application

from horey.h_logger import get_logger
from queue import Queue
logger = get_logger()


class TelegramAPI:
    """
    API to work with Grafana 8 API
    """
    def __init__(self, token=None):
        self.token = token
    
    def run_message_loop_receiver(self):
        application = Application.builder().token(self.token).build()

        # Commands
        application.add_handler(CommandHandler('start', self.start))

        # Run bot
        application.run_polling(1.0)
        return


        update_queue = Queue()
        updater = Updater(token, update_queue=update_queue)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        updater.start_polling()
        updater.idle()

    def start(self, update, context):
        """
        Start.

        :return:
        """

        user = update.effective_user
        breakpoint()
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()} 👋! I am your new bot.',
        )

    def send(self, lst_lines=None):
        pass