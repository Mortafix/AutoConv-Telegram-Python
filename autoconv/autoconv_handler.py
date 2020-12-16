from autoconv.conversation import Conversation
from autoconv.telegram_data import TelegramData
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.error import BadRequest
from re import match
from functools import reduce

class AutoConvHandler:

	def __init__(self,conversation,telegram_state_name):
		self.conversation = conversation
		self.NEXT = telegram_state_name
		self.tData = TelegramData()
		self.prev_state = None
		self.curr_state = conversation.start
		self._bkup_state_routes,self._list_keyboard = None,None

	def _build_keyboard(self,state):
		'''Build Keyboard for callback state'''
		cmd_list = [[InlineKeyboardButton(text=key_param[0][k],callback_data=k) for k in list(key_param[0].keys())[su:su+si]] for si,su in zip(key_param[1],[sum(key_param[1][:i]) for i in range(len(key_param[1]))])] if (key_param := state.callback) else [[]]
		back_button = [[InlineKeyboardButton(text=state.back_button,callback_data='BACK')]] if state.back_button and self.conversation.routes.get(state.name).get('BACK') else []
		return ((state.custom and state.custom(self.tData.prepare())) or cmd_list) + back_button

	def _next_state(self,state,value):
		'''Follow state ruote'''
		if value not in self.conversation.routes.get(state.name) and -1 not in self.conversation.routes.get(state.name): raise ValueError(f'Deafult route not found and value {value} doesn\'t exist as route of {state}.') 
		return self.conversation.routes.get(state.name).get(value) if value in self.conversation.routes.get(state.name) else self.conversation.routes.get(state.name).get(-1)

	def _change_state(self,data,state=None):
		'''Set variables for next state'''
		telegram_id = self.tData.update.effective_chat.id
		data_context = self.tData.context.user_data.get(telegram_id)
		if not state:
			state = self.conversation.get_state(self.tData.context.user_data.get(telegram_id).get('state'))
			if state.list and isinstance(data,int):
				list_idx = data if state.list_all or data < 2 else data - len(data_context.get('list'))+2 - (0,1)[data_context.get('list_i') in (0,len(data_context.get('list'))-1)]
				if state.list_all: list_idx = data if data_context.get('list_i') > data else data-1
				value = reduce(lambda x,y: x+y,self._list_keyboard)[list_idx].text
			else: value = d if (c := state.callback) and (d := c[0].get(data if not isinstance(data,int) and not data.isdigit() else int(data))) else data
			if state != self.conversation.end: self.tData.context.user_data.get(telegram_id).get('data').update({state.name:value})
			new_state = self._next_state(state,data)
		else: new_state = state
		self.prev_state,self.curr_state = self.curr_state,new_state
		data_context.update({'prev_state':self.prev_state.name,'state':new_state.name})
		if new_state.regex or new_state.handler: data_context.update({'error':False})
		elif data_context.get('error') != None: data_context.pop('error')
		return new_state

	def _wrong_message(self):
		'''Handler for wrong message'''
		telegram_id = self.tData.update.message.chat.id
		self.tData.update.message.delete()
		state = self.conversation.get_state(self.tData.context.user_data.get(telegram_id).get('state'))
		if ((self.tData.update.message.text and state.regex_error_text) or state.handler_error_text) and not self.tData.context.user_data.get(telegram_id).get('error'):
			keyboard = self._build_keyboard(state)
			self.tData.context.user_data.get(telegram_id).update({'error':True})
			self.tData.context.user_data.get(telegram_id).get('bot-msg').edit_text(f"{state.msg}\n\n{(self.tData.update.message.text and state.regex_error_text) or state.handler_error_text}",reply_markup=InlineKeyboardMarkup(keyboard),**state.kwargs)
		return self.NEXT

	def _going_back(self):
		'''Handler for back button'''
		query = self.tData.update.callback_query
		new_state = self._change_state('BACK')
		keyboard = self._build_keyboard(new_state)
		query.edit_message_text(f"{new_state}",reply_markup=keyboard,**state.kwargs)
		return self.NEXT

	def _update_dynamic_list(self,state):
		'''Update i and routes backup for dynamic list'''
		data = self.tData.context.user_data.get(self.tData.update.effective_chat.id)
		if (state_l := data.get('list')):
			i = int(data.get('list_i'))
			new_i = state_l.index(data.get('data').get(state.name)) if state.list_all else (i-1,i+1)[data.get('data').get(state.name) == state.list_buttons[1] or not i]
			data.update({'list_i':new_i})
		else:
			state_l = state.list(self.tData.prepare())
			data.update({'list':state_l,'list_i':state.list_start})
		if self._bkup_state_routes:
			back_route = self._bkup_state_routes.pop('BACK') if 'BACK' in self._bkup_state_routes else None
			self.conversation.add_routes(self.curr_state,self._bkup_state_routes,back=back_route)
			self._bkup_state_routes = None

	def _build_dynamic_routes(self,state):
		'''Build dynamic routes for current state'''
		ro,de,ba = state.routes(self.tData.prepare())
		self.conversation.add_routes(state,ro,de,ba)

	def _build_dynamic_keyboard(self,state):
		'''Build dynamic keyboard for current state'''
		keyboard = state.build(self.tData.prepare())
		keyboard,size = keyboard if isinstance(keyboard,tuple) else (keyboard,None)
		state.add_keyboard(keyboard,size,max_row=state.max_row)

	def _build_dynamic_list(self,state,keyboard):
		'''Build dynamic list for current state'''
		self._bkup_state_routes = self.conversation.routes.get(state.name)
		data = self.tData.context.user_data.get(self.tData.update.effective_chat.id)
		state_l = data.get('list')
		basic_routes = {k+len(state_l):v for k,v in self.conversation.routes.get(state.name).items() if k != 'BACK'}
		for kl in keyboard:
			for button in kl: 
				if (c := button.callback_data) and isinstance(c,int): button.callback_data += len(state_l)
		list_buttons = [InlineKeyboardButton(b,callback_data=i) for i,b in enumerate(state_l if state.list_all else state.list_buttons)]
		keyboard = [list_buttons]+keyboard
		self._list_keyboard = keyboard
		self.conversation.add_routes(state,basic_routes,default=state,back=self.conversation.routes.get(state.name).get('BACK'))
		if not state.list_all and (i := data.get('list_i')) in (0,len(state_l)-1):
			if len(state_l) < 2: keyboard.pop(0)
			else: keyboard[0].pop((1,0)[not i])
		if state.list_all and len(state_l) > 0: keyboard[data.get('list_i')//8].pop(data.get('list_i'))
		return keyboard

	def _build_dynamic_stuff(self,state): 
		'''Compute dynamic stuff: action > routes > keyboard > list'''
		data = self.tData.context.user_data.get(self.tData.update.effective_chat.id)
		if self.prev_state != self.curr_state and data.get('list'): data.pop('list'),data.pop('list_i')
		if state.list: self._update_dynamic_list(state)
		action_str = state.action(self.tData.prepare()) if state.action else None
		if state.routes: self._build_dynamic_routes(state)
		if state.build: self._build_dynamic_keyboard(state)
		keyboard = self._build_keyboard(state)
		if state.list: keyboard = self._build_dynamic_list(state,keyboard)
		reply_msg = state.msg if action_str == None else state.msg.replace('@@@',action_str)
		return InlineKeyboardMarkup(keyboard),reply_msg

	def force_state(self,state):
		'''Force a state in the conversation'''
		if isinstance(state,str): state = self.conversation.get_state(state)
		if self.tData.update and state in self.conversation.state_list:
			m = self.tData.context.user_data.get(self.tData.update.effective_chat.id).get('bot-msg')
			keyboard,reply_msg = self._build_dynamic_stuff(state)
			try:
				state = self._change_state(None,state=state)
				m.edit_text(text=f'{reply_msg}',reply_markup=keyboard,**state.kwargs)
			except BadRequest as e: 
				self.tData.exception = e
				if not match('Message is not modified',str(e)): raise e
			return self.NEXT

	def restart(self):
		'''Restart handler to initial configuration'''
		if self.tData.update:
			telegram_id = self.tData.update.effective_chat.id
			if (c := self.tData.context.user_data.get(telegram_id)):
				if (m := c.get('bot-msg')): m.delete()
				self.tData.context.user_data.pop(telegram_id)
			self.prev_state = None
			self.curr_state = self.conversation.start
		return self

	def manage_conversation(self,update,context,delete_first=False):
		'''Master function for converastion'''
		try:
			self.tData.update_telegram_data(update,context)
			telegram_id = self.tData.update.effective_chat.id
			# start
			if not self.tData.context.user_data.get(telegram_id):
				if delete_first: update.message.delete()
				state = self.conversation.start
				self.tData.context.user_data.update({telegram_id:{'prev_state':None,'state':state.name,'error':False,'data':{}}})
				keyboard,reply_msg = self._build_dynamic_stuff(state)
				msg = self.tData.update.message.reply_text(f'{reply_msg}',reply_markup=keyboard,**state.kwargs)
				self.tData.context.user_data.get(telegram_id).update({'bot-msg':msg})
				return self.NEXT
			# get data
			state = self.conversation.get_state(self.tData.context.user_data.get(telegram_id).get('state'))
			if self.tData.update.callback_query:
				data = self.tData.update.callback_query.data
				to_reply = self.tData.update.callback_query.edit_message_text
			else:
				data = (state.handler and state.handler(self.tData.prepare())) or (state.regex and self.tData.update.message.text)
				if not state.regex and not state.handler: self.tData.update.message.delete(); return self.NEXT
				if(state.regex and isinstance(data,str) and not match(state.regex,data)) or (state.handler and not data): return self._wrong_message()
				to_reply = self.tData.context.user_data.get(telegram_id).get('bot-msg').edit_text
				self.tData.update.message.delete()
			# next stage
			typed_data = state.data_type(data) if data != 'BACK' else 'BACK'
			state = self._change_state(typed_data)
			keyboard,reply_msg = self._build_dynamic_stuff(state)
			to_reply(f'{reply_msg}',reply_markup=keyboard,**state.kwargs)
			if state == self.conversation.end: self.tData.context.user_data.pop(telegram_id); return ConversationHandler.END
			return self.NEXT
		except (Exception,BadRequest) as e:
			self.tData.exception = e
			if not match('Message is not modified',str(e)):
				if self.conversation.fallback_state: return self.force_state(self.conversation.fallback_state)
				raise e
