import logging
from dotenv import dotenv_values

import telegram as tg
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from state import Dialog, SizeEnum, PaymentEnum, ConfirmEnum

API_TOKEN = dotenv_values(".env")['API_TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

    id = update.effective_user.id
    if id not in dialogs:
        dialogs[id] = Dialog(update.effective_user.send_message)

    d = dialogs[id]
    d.on_start_trigger()


dialogs = {}


def on_text_message(update: Update, context: CallbackContext) -> None:
    id = update.effective_user.id
    if id not in dialogs:
        dialogs[id] = Dialog(update.effective_user.send_message)

    d = dialogs[id]
    d.handle_message(update.message.text)


def setup_bot() -> None:
    logging.info('Connected bot: @%s' % tg.Bot(API_TOKEN).get_me()['username'])

    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, on_text_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_bot()
