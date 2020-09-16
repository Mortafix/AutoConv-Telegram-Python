import logging
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from autoconv.state import State
from autoconv.conversation import Conversation
from autoconv.autoconv_handler import AutoConvHandler

# Enable logging and port
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
BOT_TOKEN = "1281880732:AAEWIbjJOrMU7ge13lXsO7w57eia4emQED8"

#--------------------------------- Simple commands -----------------------------------

def error(update, context):
	logger.warning('Update "%s" caused error "%s"', update, context.error)

def start(update, context):
	update.message.reply_text(f'Welcome *{update.message.from_user.first_name}*!\n\nTry /example.',parse_mode='Markdown')

def handle_text(update, context):
	update.message.delete()

#--------------------------------- Example AutoConv ----------------------------------

STATE = range(1)
MARKDOWN = 'Markdown'

def comment_type(data): return '' if data == '0' else data
def recap(update,context):
	data = context.user_data.get(update.effective_chat.id).get('data')
	if (ma := 18 - data.get('age')) > 0 and data.get('consent') == 'Abort': return f'Come back when you\'ll have your *parents consent* or in *{ma}* years.'
	return '\n'.join([f'{k.title()}: *{v}*' for k,v in context.user_data.get(update.effective_chat.id).get('data').items()])

# State
name = State('name','Enter your *name*.',type=str,parse_mode=MARKDOWN)
name.add_text()
gender = State('gender','Select your *gender*',parse_mode=MARKDOWN,back=True)
gender.add_keyboard(['Male','Female','Other'])
age = State('age','Enter your *age*',parse_mode=MARKDOWN,back=True)
age.add_text(r'\d{1,2}','Enter a *valid* age')
underage = State('consent','Do you know that the responsibility will fall on your parents?',back=True)
underage.add_keyboard(['Yes','Abort'])
comment = State('comment','Do you want to enter additional comment?',type=comment_type,back=True)
comment.add_keyboard(['Nope'])
comment.add_text()
end = State('end','@@@',parse_mode=MARKDOWN)
end.add_action(recap)
# Conversation
example = Conversation(name,end_state=end)
example.add_state([gender,age,underage,comment])
example.add_routes(name,default=gender)
example.add_routes(gender,default=age,back=name)
example.add_routes(age,routes={i:underage for i in range(19)},default=comment,back=gender)
example.add_routes(underage,routes={0:comment,1:end},back=age)
example.add_routes(comment,default=end,back=age)
# Handler
autoconv = AutoConvHandler(example,STATE,back_button='Back')

def autoconv_command(update, context):
	return autoconv.manage_conversation(update,context)

# MAIN --------------------------------------------------------------------------------

def main():
	'''Bot instance'''
	updater = Updater(BOT_TOKEN, use_context=True)
	dp = updater.dispatcher

	# -----------------------------------------------------------------------
 
	# commands
	cmd_start = CommandHandler("start", start)

	# conversations
	autoconv = ConversationHandler(
		entry_points = [CommandHandler('example',autoconv_command)],
		states = {
			STATE: [MessageHandler(Filters.text,autoconv_command),CallbackQueryHandler(autoconv_command)]
		},
		fallbacks=[CommandHandler('start',start)],
		name='example-conversation'
	)

	# -----------------------------------------------------------------------

	# handlers - commands and conversations
	dp.add_handler(cmd_start)
	dp.add_handler(autoconv)

	# handlers - no command
	dp.add_handler(MessageHandler(Filters.all,handle_text))

	# handlers - error
	dp.add_error_handler(error)

	# ----------------------------------------------------------------------

	updater.start_polling()
	print('Bot started!')

	# Run the bot until you press Ctrl-C
	updater.idle()

if __name__ == '__main__':
	main()