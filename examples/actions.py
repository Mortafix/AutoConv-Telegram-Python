import logging
import sys
import traceback
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
    # logger.warning('Update "%s" caused error "%s"', update, context.error)
    trace = sys.exc_info()[2]
    traceback_error = "".join(traceback.format_tb(trace))
    print(traceback_error)


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
def current_timestamp(tdata):
    # action always takes one parameter: a TelegramData instance
    # if you want return something, must be a str
    return str(datetime.timestamp(datetime.now()))


def riddle_answer(tdata):
    # check if there is a previuos answer
    prev_answer = tdata.udata.get("riddle")
    return prev_answer != "BACK" and prev_answer or "-"


def riddle_keyboard(tdata):
    prev_answer = tdata.sdata.get("riddle")
    return ["Next"] if prev_answer and prev_answer != "BACK" else []


def log_action(tdata):
    # no return in this function
    if (answer := tdata.sdata.get("riddle")) != "0":
        tdata.udata.update({"riddle": answer})
    print(f"I just wanna log your name: {tdata.update.effective_chat.first_name}")
    # long_task(tdata.sdata)


# ---- STATES
simple = State(
    "simple",
    "This is a *simple* action.\nCurrent timestamp: *@@@*\n\nAnswer is `footsteps`",
    back_button=False,
)
# the action will replace the @@@ in the State message with its return value
simple.add_action(current_timestamp)
simple.add_keyboard(["Next"])

riddle = State(
    "riddle",
    "Try a *riddle*..\n_The more you take, the more you leave behind. What am I?_\n\nYour answer: *@@@*",
    data_type=str,
)
riddle.add_text(r"^(?i)footsteps$", "*Wrong*!")
riddle.add_action(riddle_answer)
riddle.add_dynamic_keyboard(riddle_keyboard)

log = State("log", "In this state there is a *hidden task* with a terminal log")
log.add_action(log_action)
log.add_keyboard(["Next"])

end = State("end", "This is the *end*.")


# ---- CONVERSATION
conv = Conversation(simple)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(simple, default=riddle)
conv.add_routes(riddle, default=log, back=simple)
conv.add_routes(log, default=end, back=riddle)
conv.add_routes(end, back=log)


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
