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
def custom_dynamic_keyboard(tdata):
    # need to return a keyboard as list or dict
    state_value = tdata.sdata.get("dynamic")
    return ["Go back to go forward"] if state_value is None else ["Now you can go"]


# ---- STATES
static = State("static", "This State has a *simple static keyboard*.")
static.add_keyboard(["Next"])

static_dict = State(
    "static_dict", "This is another static keyboard, but defined with a *dictionary*."
)
static_dict.add_keyboard({42: "Go back", 99: "Next"})

dynamic = State("dynamic", "This is a *dynamic keyboard* changed by a custom function.")
dynamic.add_dynamic_keyboard(custom_dynamic_keyboard)

end = State("end", "This is the *end*.")


# ---- DYNAMIC
def dynamic_routes_for_keyboard(tdata):
    # need to return a tuple: Routes, Default, back
    state_value = tdata.sdata.get("dynamic")
    return (None, static_dict if state_value is None else end, None)


# ---- CONVERSATION
conv = Conversation(static, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"})
conv.add_routes(static, default=static_dict)
# same as -> conv.add_routes(static, routes={0: static_dict})
conv.add_routes(static_dict, routes={42: static, 99: dynamic}, back=static)
dynamic.add_dynamic_routes(dynamic_routes_for_keyboard)

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
