import datetime
import logging
import os

from telegram import Update
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext

logger = logging.getLogger(__name__)

USER_LOG_FILE = "./ls-messages.txt"
LOG_FILE = "./app.log"

msg_format = (
    "Квартира/Машиноместо/Коммерческое помещение XXX обращение XXXXXXX\n\n"
    "Если вы владеете несколькими объектами недвижимости, отправьте информацию "
    "по каждому из них отдельными сообщениями."
)

WELCOME_MESSAGE = f"""Добро пожаловать!
Зарегистрируйте своё обращение в МЖИ ответным сообщением в формате:

{msg_format}"""

CONFIRM_TEXT = "Спасибо! Мы сохранили вашу информацию."
ERROR_TEXT = f"Ошибка. Напишите сообщение в формате:\n\n{msg_format}"


def log(msg):

    with open(LOG_FILE, "+a") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")

def log_message(message):
    if not message.text:
        raise Exception("No text provided!")

    msg = f"{datetime.datetime.now()}: FROM {message.from_user.full_name}: {message.text}\n"
    with open(USER_LOG_FILE, "+a") as f:
        f.write(msg)


def start(update: Update, context: CallbackContext):

    log(f"{update.message.from_user.full_name} called /start")
    update.message.reply_text(WELCOME_MESSAGE)


def main_handle(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    log(f"{update.message.from_user.full_name} wrote {update.message.text}")
    try:
        log_message(update.message)
    except Exception as e:
        log(e)
        context.bot.send_message(update.message.chat_id, ERROR_TEXT)
        return
    else:
        context.bot.send_message(update.message.chat_id, CONFIRM_TEXT)


def main() -> None:
    updater = Updater(os.getenv("TG_TOKEN"))

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    # Register commands
    # Echo any message that is not a command
    dispatcher.add_handler(MessageHandler(~Filters.command, main_handle))

    # Start the Bot
    updater.start_polling()

    log("Bot started.")

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
