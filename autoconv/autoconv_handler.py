from autoconv.conversation import Conversation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from re import match

class AutoConvHandler:

	def __init__(self,conversation,telegram_state_name,back_button=None):
		self.conversation = conversation
		self.NEXT = telegram_state_name
		self.back = back_button

	def _build_keyboard(self,state):
		'''Build Keyboard for callback state'''
		cmd_list = [[InlineKeyboardButton(text=key_param[0][i+su],callback_data=i+su) for i in range(si)] for si,su in zip(key_param[1],[sum(key_param[1][:i]) for i in range(len(key_param[1]))])] if (key_param := state.callback) else [[]]
		if self.back and state not in (self.conversation.start,self.conversation.end): cmd_list += [[InlineKeyboardButton(text=self.back,callback_data='BACK')]]
		return InlineKeyboardMarkup(cmd_list) 

	def _next_state(self,state,value):
		'''Follow state ruote'''
		if value not in self.conversation.routes.get(state.name) and -1 not in self.conversation.routes.get(state.name): raise ValueError(f'Value {value} don\'t exists as route of {state}, neither a default route.') 
		return self.conversation.routes.get(state.name).get(value) if value in self.conversation.routes.get(state.name) else self.conversation.routes.get(state.name).get(-1)

	def _change_state(self,telegram_id,data):
		'''Set variables for next state'''
		state = self.context.user_data.get(telegram_id).get('state')
		value = state.callback[0][data] if state.callback and state.callback[0].get(data) else data
		if state != self.conversation.end: self.context.user_data.get(telegram_id).get('data').update({state.name:value})
		new_state = self._next_state(state,data)
		self.context.user_data.get(telegram_id).update({'state':new_state,'error':False})
		return new_state

	def _wrong_text(self):
		'''Handler for wrong regex in text state'''
		telegram_id = self.update.message.chat.id
		self.update.message.delete()
		state = self.context.user_data.get(telegram_id).get('state')
		if state.text and not self.context.user_data.get(telegram_id).get('error'):
			keyboard = self._build_keyboard(state)
			self.context.user_data.get(telegram_id).update({'error':True})
			self.context.user_data.get(telegram_id).get('bot-msg').edit_text(f"{state.msg}\n\n{state.text[1]}",reply_markup=keyboard,parse_mode=state.mode)
		return self.NEXT

	def _going_back(self):
		'''Handler for back button'''
		query = self.update.callback_query
		telegram_id = self.update.callback_query.message.chat.id
		new_state = self._change_state(telegram_id,'BACK')
		keyboard = self._build_keyboard(new_state)
		query.edit_message_text(f"{new_state}",reply_markup=keyboard,parse_mode=new_state.mode)
		return self.NEXT

	def manage_conversation(self,update,context):
		'''Master function for converastion'''
		self.update = update
		self.context = context
		telegram_id = self.update.effective_chat.id
		# start
		if not self.context.user_data.get(telegram_id):
			state = self.conversation.start
			keyboard = self._build_keyboard(state)
			msg = self.update.message.reply_text(f'{state.msg}',reply_markup=keyboard,parse_mode=state.mode)
			self.context.user_data.update({telegram_id:{'state':state,'error':False,'bot-msg':msg,'data':{}}})
			return self.NEXT
		# get data
		state = self.context.user_data.get(telegram_id).get('state')
		if self.update.callback_query:
			data = self.update.callback_query.data
			to_reply = self.update.callback_query.edit_message_text
		else:
			data = self.update.message.text
			if not state.text: self.update.message.delete(); return self.NEXT
			if not match(state.text[0],data): return self._wrong_text()
			to_reply = self.context.user_data.get(telegram_id).get('bot-msg').edit_text
			self.update.message.delete()
		# next stage
		typed_data = state.data_type(data) if data != 'BACK' else 'BACK'
		state = self._change_state(telegram_id,typed_data)
		keyboard = self._build_keyboard(state)
		ret = state.action(self.update,self.context) if state.action else None
		msg = state.msg if ret == None else state.msg.replace('@@@',ret)
		to_reply(f'{msg}',reply_markup=keyboard,parse_mode=state.mode)
		if state == self.conversation.end: context.user_data.update({telegram_id:None}); return ConversationHandler.END
		return self.NEXT