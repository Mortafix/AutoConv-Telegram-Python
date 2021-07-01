import logging

from autoconv.autoconv_handler import AutoConvHandler
from autoconv.conversation import Conversation
from autoconv.state import State
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)

# Enable logging and port
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --------------------------------- Simple commands -----------------------------------


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    update.message.reply_text(
        f"Welcome *{update.message.from_user.first_name}*!\n\nTry /example.",
        parse_mode="Markdown",
    )


def handle_text(update, context):
    update.message.delete()


# --------------------------------- Example AutoConv ----------------------------------

STATE = range(1)

# ---- STATES
first = State("first", back_button=False)
first.add_keyboard(["Next"])

second = State("second")
second.add_keyboard(["Next"])

third = State("third")
third.add_keyboard(["Next"])

end = State("end")

# ---- CONVERSATION
texts = {
    "first": "This is the message for the *first* state!",
    "second": "Another text specified in the *dictionary*..",
    "third": "You can define texts in an _external file_\nFormat supported: *JSON*, *YAML* or *TOML*.",
    "end": "This is the *end*.",
}
# it can be also a file (specified via filename) in json, yaml or toml
conv = Conversation(first, end_state=end, state_messages=texts)
conv.set_defaults(params={"parse_mode": "Markdown"})
conv.add_routes(first, default=second)
conv.add_routes(second, default=third, back=first)
conv.add_routes(third, default=end, back=second)


# ---- HANDLER
autoconv = AutoConvHandler(conv, STATE)


def autoconv_command(update, context):
    return autoconv.manage_conversation(update, context)


# MAIN --------------------------------------------------------------------------------


def main():
    """Bot instance"""
    updater = Updater("1579494237:AAHw6nQfRBboYvD-PKB1mV4W0WUDoHtuPMc")
    dp = updater.dispatcher

    # -----------------------------------------------------------------------

    # commands
    cmd_start = CommandHandler("start", start)

    # conversations
    autoconv = ConversationHandler(
        entry_points=[CommandHandler("example", autoconv_command)],
        states={
            STATE: [
                MessageHandler(Filters.text, autoconv_command),
                CallbackQueryHandler(autoconv_command),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        name="example-conversation",
    )

    # -----------------------------------------------------------------------

    # handlers - commands and conversations
    dp.add_handler(cmd_start)
    dp.add_handler(autoconv)

    # handlers - no command
    dp.add_handler(MessageHandler(Filters.all, handle_text))

    # handlers - error
    dp.add_error_handler(error)

    # ----------------------------------------------------------------------

    updater.start_polling()
    print("Bot started!")

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == "__main__":
    main()
