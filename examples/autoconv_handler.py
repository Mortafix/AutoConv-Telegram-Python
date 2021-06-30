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
def log_user(tdata):
    chat = tdata.update.effective_chat
    print(
        "> A user tried to access the bot: "
        f"{chat.username or chat.first_name} ({chat.id})"
    )


def new_users_list(tdata):
    new_user = tdata.sdata.get("add")
    return tdata.users + [new_user]


def get_users_list(tdata):
    # action happens before the refresh auth, so here we have the pre-refresh list
    new_user = tdata.sdata.get("add")
    new_list = tdata.users + [new_user]
    return "\n".join(map(str, new_list))


# ---- STATES
help_state = State("help", "Nice *Help*.. or maybe not!", back_button=False)
help_state.add_keyboard(["Menu"])

simple = State(
    "simple", "Another *useless* state\nyou can use /help anytime", back_button=False
)
simple.add_keyboard(["Next"])

restart = State(
    "restart", "You can also use /help here!\nRemember also to *restart* with /restart"
)
restart.add_keyboard(["Next"])

end = State("end", "This is the *end*.", back_button=False)

# ---- CONVERSATION
conv = Conversation(simple, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(simple, default=restart)
conv.add_routes(restart, default=end, back=simple)
conv.add_routes(help_state, default=simple)
conv.add_routes(end)


# ---- HANDLER
autoconv = AutoConvHandler(conv, STATE)
# you need to define a placeholder (STATE in this case) in order to work


def autoconv_command(update, context):
    return autoconv.manage_conversation(update, context)


def restart(update, context):
    # simple command handler to restart the conversation
    autoconv.restart(update, context)
    return autoconv.manage_conversation(update, context, delete_first=True)


def help_handler(update, context):
    # simple command handler to force the help state
    update.message.delete()
    return autoconv.force_state("help", update)


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
                CommandHandler("restart", restart),
                CommandHandler("help", help_handler),
                MessageHandler(Filters.sticker, autoconv_command),
                MessageHandler(Filters.photo, autoconv_command),
                MessageHandler(Filters.video, autoconv_command),
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
