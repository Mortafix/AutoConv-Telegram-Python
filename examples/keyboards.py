import logging

from autoconv.autoconv_handler import AutoConvHandler
from autoconv.conversation import Conversation
from autoconv.state import State
from telegram import InlineKeyboardButton
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
def dynamic_keyboard(tdata):
    # need to return a keyboard as list or dict
    state_value = tdata.sdata.get("dynamic")
    return ["Go back to go forward"] if state_value is None else ["Now you can go"]


def custom_keyboard(tdata):
    # need to return a list of InlineKyeboardButton
    msg = "This is an example.. it doens't work."
    return [
        [InlineKeyboardButton("Share", switch_inline_query=msg)],
        [InlineKeyboardButton("Next", callback_data=0)],
    ]


def counter_keyboard(tdata):
    # show the next button only if the counter == 5
    if tdata.udata.get("counter") == 5:
        return ["+1", "-1", "Next"], (2, 1)
    return ["+1", "-1"]


def show_counter(tdata):
    # create the counter and show it
    if not tdata.udata.get("counter"):
        tdata.context.user_data.update({"counter": 0})
    return str(tdata.udata.get("counter"))


def change_counter(tdata, add):
    # change the value of the counter
    counter = tdata.udata.get("counter")
    value = 1 if add else -1
    tdata.context.user_data.update({"counter": counter + value})


def sub_counter(tdata):
    change_counter(tdata, False)


def add_counter(tdata):
    change_counter(tdata, True)


# ---- STATES
static = State("static", "This State has a *simple static keyboard*.")
static.add_keyboard(["Next"])

static_dict = State(
    "static_dict", "This is another static keyboard, but defined with a *dictionary*."
)
static_dict.add_keyboard({42: "Go back", 99: "Next"})

dynamic = State("dynamic", "This is a *dynamic keyboard* changed by a custom function.")
dynamic.add_dynamic_keyboard(dynamic_keyboard)

custom = State(
    "custom", "This is the most powerful, but dangerous keyboard..\nthe *custom* one."
)
custom.add_custom_keyboard(custom_keyboard)

operation = State(
    "operation",
    "These are *operations button* that trigger functions without change the state\nGo to *5* to continue..\n\nCounter: *@@@*",
)
operation.add_dynamic_keyboard(counter_keyboard)
operation.add_action(show_counter)
operation.add_operation_buttons([add_counter, sub_counter])
# same as a dict -> operation.add_button_operations({0: add_counter, 1: sub_counter})

end = State("end", "This is the *end*.")


# ---- DYNAMIC
def keyboard_dynamic_routes(tdata):
    # need to return a tuple: Routes, Default, back
    state_value = tdata.sdata.get("dynamic")
    return (None, static_dict if state_value is None else custom, None)


# ---- CONVERSATION
conv = Conversation(static, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"})
conv.add_routes(static, default=static_dict)
# same as -> conv.add_routes(static, routes={0: static_dict})
conv.add_routes(static_dict, routes={42: static, 99: dynamic}, back=static)
dynamic.add_dynamic_routes(keyboard_dynamic_routes)
conv.add_routes(custom, default=operation)
conv.add_routes(operation, routes={2: end}, back=custom)

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
