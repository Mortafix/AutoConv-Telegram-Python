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
BOT_TOKEN = "BOT-TOKEN"

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
MARKDOWN = "Markdown"
BACK = "Back"


# ---- FUNCS
def comment_type(data):
    return "" if data == "0" else data


def recap(tdata):
    if (ma := 18 - tdata.sdata.get("age")) > 0 and tdata.sdata.get(
        "consent"
    ) == "Abort":
        return f"Come back when you'll have your *parents consent* or in *{ma}* years."
    return "\n".join([f"{k.title()}: *{v}*" for k, v in tdata.sdata.items()])


def add_timestamp(text):
    return f"({datetime.now():%H:%M})\n\n{text}"


# ---- STATES
name = State("name", "Enter your *name*.", data_type=str, back_button=False)
name.add_text()
gender = State("gender", "Select your *gender*", back_button="< Another back")
gender.add_keyboard(["Male", "Female", "Other"])
age = State("age", "Enter your <b>age</b>", parse_mode="html")
age.add_text(r"\d{1,2}", "Enter a *valid* age")
underage = State("consent", "Drop the _responsibility_ on your parents?")
underage.add_keyboard(["Yes", "Abort"])
comment = State(
    "comment", "Do you want to enter additional comment?", data_type=comment_type
)
comment.add_keyboard(["Nope"])
comment.add_text()
end = State("end", "@@@", back_button=False)
end.add_action(recap)

# ---- CONVERSATION
conv = Conversation(name, end_state=end)
conv.set_defaults(
    params={"parse_mode": MARKDOWN, "disable_web_page_preview": True},
    function=add_timestamp,
    back_button=BACK,
)
conv.add_routes(name, default=gender)
conv.add_routes(gender, default=age, back=name)
conv.add_routes(
    age, routes={i: underage for i in range(19)}, default=comment, back=gender
)
conv.add_routes(underage, routes={0: comment, 1: end}, back=age)
conv.add_routes(comment, default=end)
conv.add_routes(end)

# ---- HANDLER
autoconv = AutoConvHandler(conv, STATE)


def autoconv_command(update, context):
    return autoconv.manage_conversation(update, context)


# MAIN --------------------------------------------------------------------------------


def main():
    """Bot instance"""
    updater = Updater(BOT_TOKEN)
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
