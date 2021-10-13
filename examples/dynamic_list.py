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
def simple_list(tdata):
    return ["First element", "Second elem", "Another one", "One more", "Opsie"]


def labels_list(tdata):
    return ["First", "Second", "Another", "More", "Ops"]


def show_current_element(tdata):
    return tdata.udata.get("list_el")
    # same as -> return tdata.udata.get("list")[tdata.udata.get("list_i")]


def last_elem_keyboard(tdata):
    i = tdata.udata.get("list_i")
    return i == 4 and ["Next"] or []


# ---- STATES
simple = State("simple", "This is the *current* element\n\n*@@@*", back_button=False)
simple.add_dynamic_list(simple_list)
simple.add_action(show_current_element)
simple.add_keyboard(["Next"])

showall = State(
    "showall",
    "This is the *current* element\nTo go in the next State, go to _Ops_...\n\n*@@@*",
)
showall.add_dynamic_list(simple_list, all_elements=True, labels=labels_list, max_row=2)
showall.add_action(show_current_element)
showall.add_dynamic_keyboard(last_elem_keyboard)

strange = State("strange", "This is the *current* element\n\n*@@@*")
strange.add_dynamic_list(simple_list, start=3, left_button="<<!", right_button="next?")
strange.add_action(show_current_element)
strange.add_keyboard(["Next"])

preserve = State(
    "preserve",
    "This dynamic list *preserve the index*, trying to go back\n\nCurrent: *@@@*",
)
preserve.add_dynamic_list(simple_list, preserve_index=True)
preserve.add_action(show_current_element)
preserve.add_keyboard(["Next"])

end = State("end", "This is the *end*.", back_button=False)


# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(simple, routes={0: showall}, default=simple)
conv.add_routes(showall, routes={0: strange}, default=showall, back=simple)
conv.add_routes(strange, routes={0: preserve}, default=strange, back=showall)
conv.add_routes(preserve, routes={0: end}, default=preserve, back=strange)


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
