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
def sticker_handler(tdata):
    sticker = tdata.update.message.sticker
    if not sticker:
        return None
    return sticker.file_unique_id


def image_handler(tdata):
    images = tdata.update.message.photo
    if not images:
        return None
    return ", ".join(im.file_unique_id for im in images)


def video_handler(tdata):
    video = tdata.update.message.video
    if not video:
        return None
    return video.file_unique_id


def print_recap(tdata):
    return "\n".join(f"{key}: *{value}*" for key, value in tdata.sdata.items())


# ---- STATES
sticker = State(
    "sticker", "This is a *sticker* handler", back_button=False, data_type=str
)
sticker.add_custom_handler(sticker_handler, "This is not a sticker!")

image = State("image", "This is an *image* handler", data_type=str)
image.add_custom_handler(image_handler, "This is not an image!")

video = State("video", "This is a *video* handler", data_type=str)
video.add_custom_handler(video_handler, "This is not a video!")

end = State("end", "This is the *end* with a *recap*\n\n@@@", back_button=False)
end.add_action(print_recap)

# ---- CONVERSATION
conv = Conversation(sticker, end_state=end)
conv.set_defaults(params={"parse_mode": "Markdown"}, back_button="Back")
conv.add_routes(sticker, default=image)
conv.add_routes(image, default=video, back=sticker)
conv.add_routes(video, default=end, back=image)


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
