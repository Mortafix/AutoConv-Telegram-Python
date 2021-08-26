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
def save_variables(tdata):
    # different method to save data
    tdata.save(start=True)
    tdata.save({"level": 1, "array": [1, None, "hey"]})
    tdata.save([("another", 42), ("wow", "opsie")])


def count_action(tdata):
    number = tdata.sdata.get("count")
    tdata.get_or_set("counter", 0)
    inserted_value = isinstance(number, int) and number or 0
    return tdata.add("counter", inserted_value)


def sequence_action(tdata):
    names = {"f": "Flowy", "b": "Ball", "t": "Toastum"}
    seq = tdata.get_or_set("seq", "")
    return ", ".join(map(lambda x: names.get(x), seq))


def sequence_keyboard(tdata):
    seq = tdata.udata.get("seq")
    if seq == "ttfb":
        return {4: "Next"}
    if len(seq) > 0:
        return ["Flower", "Ballon", "Toast", "Delete"]
    return ["Flower", "Ballon", "Toast"]


# ---- STATES
simple = State(
    "simple", "In this state, I'm going to *save* some value", back_button=False
)
simple.add_action(save_variables)
simple.add_keyboard(["Next"])

count = State("count", "Insert a number to *increment* the counter\n\nCounter: *@@@*")
count.add_action(count_action)
count.add_text(r"^\d+(?<!0)$", "Insert a _valid_ number")
count.add_keyboard(["Next"])

sequence = State(
    "sequence", "Insert the *sequence*:\n`toast, toast, flower, ballon`\n\n@@@"
)
sequence.add_dynamic_keyboard(sequence_keyboard)
sequence.add_action(sequence_action)
sequence.add_operation_buttons(
    [
        lambda x: x.add("seq", "f"),
        lambda x: x.add("seq", "b"),
        lambda x: x.add("seq", "t"),
        lambda x: x.save(seq=x.udata.get("seq")[:-1]),
    ]
)

end = State("end", "This is the *end*.")


# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(simple, default=count)
conv.add_routes(count, default=count, routes={0: sequence})
conv.add_routes(sequence, default=sequence, routes={4: end})


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
