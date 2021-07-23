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

autoconv, STATE = range(2)


# ---- FUNCS
def go_to_next(tdata):
    tdata.autoconv.set_timed_function(3, "log")


def print_name(tdata):
    print(f"User is {tdata.update.effective_chat.first_name} :|=")


def log_values(tdata):
    tdata.autoconv.set_timed_function(5, function=print_name)


def bomb_explosion(tdata):
    tdata.autoconv.set_timed_function(3, "bomb")


def defuse_bomb(tdata):
    tdata.autoconv.stop_timed_function("bomb")
    # if you are fast enough you can stop the console log
    tdata.autoconv.stop_timed_function(function=print_name)


def show_password(tdata):
    # you can pass every kwargs you want
    tdata.autoconv.send_autodestroy_message(
        "The *password* is `pink-elephant-42`!", 2, parse_mode="Markdown"
    )


# ---- STATES
simple = State(
    "simple",
    "This is simple *timer*!\nIn *3 seconds* you will redirect to the next state..",
    back_button=False,
)
simple.add_action(go_to_next)

log = State("log", "In this state in 5 seconds you will receive a *console log*")
log.add_action(log_values)
log.add_keyboard(["Next"])

run = State(
    "run",
    "_Run Barry, run!_\nThe bomb will *explode* in 3 seconds..",
    back_button=False,
)
run.add_action(bomb_explosion)
run.add_keyboard(["Run"])

run_continue = State("run_continue", "*RUUUUUN!*", back_button=False)
run_continue.add_keyboard(["...", "Gun", "!?", "Run", ":O"])

bomb = State("bomb", "_KABOOOOM!?!_", back_button=False)
bomb.add_keyboard(["Begin"])

password = State(
    "password",
    "This state will send a message that will *autodestroy* itself in 2 seconds",
)
password.add_action(defuse_bomb)
password.add_keyboard(["Next", "Show password"], (1, 1))
password.add_operation_buttons({1: show_password})

end = State("end", "This is the *end*.")


# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(log, default=run)
conv.add_routes(run, default=run_continue)
conv.add_routes(run_continue, routes={3: password}, default=run_continue)
conv.add_routes(password, routes={0: end}, back=run)
conv.add_routes(bomb, default=simple)

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
