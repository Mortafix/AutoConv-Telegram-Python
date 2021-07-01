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


# ---- FUNCS
def error_handler(tdata):
    print(f"Error: {tdata.exception}")
    return str(tdata.exception)


# ---- STATES
errors = State(
    "error", "Opsie, it seems an *error* occured..\n\n`@@@`", back_button=False
)
errors.add_keyboard(["Menu"])
errors.add_action(error_handler)

menu = State("menu", "Choose carefully, something is _broken_...", back_button=False)
menu.add_keyboard(["Safe state", "Sus state"])

divisonbyzero = State("division", "I want to divide 42 by 0... result=@@@")
divisonbyzero.add_action(lambda _: 42 / 0)
divisonbyzero.add_keyboard(["Next"])

end = State("end", "This is the *end*.", back_button=False)

# ---- CONVERSATION
conv = Conversation(menu, end_state=end, fallback_state=errors)
# a Conversation will run forever, except if it has an end State
# error state is a State that catches all the exceptions in autoconv
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(errors, default=menu)
conv.add_routes(menu, routes={0: end, 1: divisonbyzero})
conv.add_routes(divisonbyzero, default=end, back=menu)


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
