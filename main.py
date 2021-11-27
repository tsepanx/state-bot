import logging

from dotenv import dotenv_values
import telegram as tg
from telegram import Update, ForceReply, User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from state import Dialog

API_TOKEN = dotenv_values(".env")['API_TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


dialogs = {}


def get_user_dialog(user: User):
    if user.id not in dialogs:
        dialogs[user.id] = Dialog(user.send_message)

    return dialogs[user.id]


def start_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

    d = get_user_dialog(user)

    d.machine.set_state('start')
    d.on_start_trigger()


def on_text_message(update: Update, context: CallbackContext) -> None:
    d = get_user_dialog(update.effective_user)

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
