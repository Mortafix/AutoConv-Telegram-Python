import logging
from datetime import datetime
from random import choice
from re import match
from time import sleep

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
def current_timestamp(tdata):
    # action always takes one parameter: a TelegramData instance
    # if you want return something, must be a str
    return str(datetime.timestamp(datetime.now()))


def riddle_answer(tdata):
    # check if there is a previuos answer
    prev_answer = tdata.sdata.get("riddle")
    return prev_answer not in ("BACK", "0") and prev_answer or "-"


def riddle_keyboard(tdata):
    prev_answer = tdata.sdata.get("riddle", "")
    return ["Next"] if match(r"^(?i)footsteps$", str(prev_answer)) else []


def get_counter(tdata):
    return tdata.udata.get("error-counter", 0)


def build_answer(tdata):
    counter = get_counter(tdata)
    if counter > 10:
        return ".*", "Sorry for bothering you, you can answer everything you want now"
    return (
        counter,
        "Don't worry, first time" if counter <= 1 else "Ops, it's more than one!",
    )


def log_action(tdata):
    # no return in this function
    sleep(1.5)  # long_task(tdata.sdata)
    if (answer := tdata.sdata.get("riddle")) != "0":
        tdata.udata.update({"riddle-answer": answer})
    print(f"I just wanna log your name: {tdata.update.effective_chat.first_name}")


def go_to_random(tdata):
    # you can use force state (from tdata.autoconv) to force a state
    # it works in operations button and in action too
    random_state = choice(tdata.autoconv.conversation.state_list)
    print(f"> Going to {random_state}")
    tdata.context.user_data.get("data").clear()
    tdata.autoconv.force_state(random_state, tdata.update)
    # always use EXIT_SIGNAL to interrupt autoconv
    # if you don't use EXIT_SIGNAL, Autoconv will continue as normal (not intended)
    return tdata.autoconv.EXIT_SIGNAL


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

dynamic = State(
    "dynamic",
    "This is a *dynamic* riddle\n_The answer is always the counter_\nWrong answers counter: *@@@*",
    data_type=str,
)
dynamic.add_action(get_counter)
dynamic.add_dynamic_text(build_answer)

log = State("log", "In this state there is a *hidden task* with a terminal log")
log.add_action(log_action)
log.add_keyboard(["Next"])
# this will send a message while the main task is running
log.set_long_task("Computing...")

force = State("force", "This state has an *advanced features*, check out the code!")
force.add_keyboard(["Next", "Go to a random state"])
force.add_operation_buttons({1: go_to_random})

end = State("end", "This is the *end*.")


# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(simple, default=riddle)
conv.add_routes(riddle, default=dynamic, back=simple)
conv.add_routes(dynamic, default=log, back=riddle)
conv.add_routes(log, default=force, back=dynamic)
conv.add_routes(force, default=end, back=log)


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
