import logging
from datetime import datetime

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


# ---- FUNCS
def set_timestamp(message):
    current_timestamp = datetime.timestamp(datetime.now())
    return f"Now: {int(current_timestamp)}\n\n{message}"


# ---- STATES
simple = State(
    "simple",
    "This is a *simple* state with all the default\nLike the web preview for [links](https://github.com/Mortafix/AutoConv-Telegram-Python)",
    back_button=False,
)
# I need to set back_button to False beacause I set a default back button in the Conversation
simple.add_keyboard(["Next"])

opponent = State(
    "opponent",
    "I want to go against the <i>default</i>.. Go <u>HTML</u>!",
    parse_mode="html",
    disable_web_page_preview=False,
    back_button="My back button :ç",
)
# Every arguments here override the Conversation defaults
opponent.add_keyboard(["Next"])

sheep = State("sheep", "Another *default* State, 2nd _sheep_..")
sheep.add_keyboard(["Next"])

end = State("end", "This is the *end*.", back_button=False)

# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(
    params={"parse_mode": "Markdown", "disable_web_page_preview": True},
    func=set_timestamp,
    back_button="Back",
)
conv.add_routes(simple, default=opponent)
conv.add_routes(opponent, default=sheep, back=simple)
conv.add_routes(sheep, default=end, back=opponent)
conv.add_routes(end)


# ---- HANDLER
autoconv = AutoConvHandler(conv, STATE)


def autoconv_command(update, context):
    return autoconv.manage_conversation(update, context)


# MAIN --------------------------------------------------------------------------------


def main():
    """Bot instance"""
    updater = Updater("BOT-TOKEN")
    dp = updater.dispatcher

    # -----------------------------------------------------------------------

    # commands
    cmd_start = CommandHandler("start", start)

    # conversations
    autoconv = ConversationHandler(
        entry_points=[CommandHandler("example", autoconv_command)],
        states={
            STATE: [
                MessageHandler(Filters.all, autoconv_command),
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
