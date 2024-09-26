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

GROUP_ID = None
ADMIN_ID = None


def log(msg):

    with open(LOG_FILE, "+a") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")


def log_message(context: CallbackContext, message):
    if not message.text:
        raise Exception("No text provided!")

    msg = (
        f"{datetime.datetime.now()}: FROM {message.from_user.full_name} "
        "(ID={message.from_user.id}): {message.text}\n"
    )
    with open(USER_LOG_FILE, "+a") as f:
        f.write(msg)

    if GROUP_ID is not None:
        context.bot.forward_message(GROUP_ID, message.chat.id, message.message_id)
        log(f"Message forwarded to GROUP {GROUP_ID}")


def start(update: Update, context: CallbackContext):

    log(f"USERID={update.message.from_user.id} {update.message.from_user.full_name} called /start")
    update.message.reply_text(WELCOME_MESSAGE)


def report(update: Update, context: CallbackContext):
    log(f"USERID={update.message.from_user.id} {update.message.from_user.full_name} called /report")
    if ADMIN_ID is not None:
        with open(USER_LOG_FILE, "r") as f:
            text = f.read()
        context.bot.send_message(ADMIN_ID, text)
    else:
        log("Got report command, but ADMIN_ID is not set.")


def main_handle(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    log(
        f"USERID={update.message.from_user.id} {update.message.from_user.full_name} wrote "
        "{update.message.text}"
    )
    try:
        log_message(context, update.message)
    except Exception as e:
        log(e)
        context.bot.send_message(update.message.chat_id, ERROR_TEXT)
        return
    else:
        context.bot.send_message(update.message.chat_id, CONFIRM_TEXT)


def main() -> None:
    updater = Updater(os.getenv("TG_TOKEN"))

    global GROUP_ID
    try:
        GROUP_ID = os.getenv("TG_GROUP_ID")
        log(f"Initialized GROUP_ID: {GROUP_ID}")
    except Exception as e:
        log(e)

    global ADMIN_ID
    try:
        ADMIN_ID = os.getenv("TG_ADMIN_ID")
        log(f"Initialized ADMIN_ID: {ADMIN_ID}")
    except Exception as e:
        log(e)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("report", report))

    # Register commands
    # Echo any message that is not a command
    dispatcher.add_handler(MessageHandler(~Filters.command, main_handle))

    # Start the Bot
    updater.start_polling()

    log("Bot started.")

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == "__main__":
    main()
