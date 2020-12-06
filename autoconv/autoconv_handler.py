from autoconv.conversation import Conversation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from re import match
from functools import reduce

class AutoConvHandler:

	def __init__(self,conversation,telegram_state_name,back_button='Back'):
		self.conversation = conversation
		self.NEXT = telegram_state_name
		self.back_button = back_button
		self.prev_state = None
		self.curr_state = conversation.start
		self.update, self.context = None, None
		self._bkup_state_routes,self._bkup_state_keyboard = None,None

	def _build_keyboard(self,state):
		'''Build Keyboard for callback state'''
		cmd_list = [[InlineKeyboardButton(text=key_param[0][k],callback_data=k) for k in list(key_param[0].keys())[su:su+si]] for si,su in zip(key_param[1],[sum(key_param[1][:i]) for i in range(len(key_param[1]))])] if (key_param := state.callback) else [[]]
		if state.back: cmd_list += [[InlineKeyboardButton(text=self.back_button,callback_data='BACK')]]
		return (state.custom and state.custom(self.update,self.context)) or cmd_list

	def _next_state(self,state,value):
		'''Follow state ruote'''
		if value not in self.conversation.routes.get(state.name) and -1 not in self.conversation.routes.get(state.name): raise ValueError(f'Deafult route not found and value {value} doesn\'t exist as route of {state}.') 
		return self.conversation.routes.get(state.name).get(value) if value in self.conversation.routes.get(state.name) else self.conversation.routes.get(state.name).get(-1)

	def _change_state(self,telegram_id,data):
		'''Set variables for next state'''
		data_context = self.context.user_data.get(telegram_id)
		state = self.conversation.get_state(self.context.user_data.get(telegram_id).get('state'))
		if state.list:
			list_idx = data if state.list_all or data < 2 else data - len(data_context.get('list'))+2 - (0,1)[data_context.get('list_i') in (0,len(data_context.get('list'))-1)]
			if state.list_all: list_idx = data if data_context.get('list_i') > data else data-1
			value = reduce(lambda x,y: x+y,self.list_keyboard)[list_idx].text
		else: value = d if (c := state.callback) and (d := c[0].get(data)) else data
		if state != self.conversation.end: self.context.user_data.get(telegram_id).get('data').update({state.name:value})
		new_state = self._next_state(state,data)
		self.prev_state,self.curr_state = self.curr_state,new_state
		data_context.update({'prev_state':self.prev_state.name,'state':new_state.name})
		if new_state.text: data_context.update({'error':False})
		elif data_context.get('error') != None: data_context.pop('error')
		return new_state

	def _wrong_text(self):
		'''Handler for wrong regex in text state'''
		telegram_id = self.update.message.chat.id
		self.update.message.delete()
		state = self.conversation.get_state(self.context.user_data.get(telegram_id).get('state'))
		if state.text and not self.context.user_data.get(telegram_id).get('error'):
			keyboard = self._build_keyboard(state)
			self.context.user_data.get(telegram_id).update({'error':True})
			self.context.user_data.get(telegram_id).get('bot-msg').edit_text(f"{state.msg}\n\n{state.text[1]}",reply_markup=InlineKeyboardMarkup(keyboard),parse_mode=state.mode)
		return self.NEXT

	def _going_back(self):
		'''Handler for back button'''
		query = self.update.callback_query
		telegram_id = self.update.callback_query.message.chat.id
		new_state = self._change_state(telegram_id,'BACK')
		keyboard = self._build_keyboard(new_state)
		query.edit_message_text(f"{new_state}",reply_markup=keyboard,parse_mode=new_state.mode)
		return self.NEXT

	def _update_dynamic_list(self,state):
		'''Update i and routes backup for dynamic list'''
		data = self.context.user_data.get(self.update.effective_chat.id)
		if (state_l := data.get('list')):
			i = int(data.get('list_i'))
			new_i = state_l.index(data.get('data').get(state.name)) if state.list_all else (i-1,i+1)[data.get('data').get(state.name) == state.list_buttons[1] or not i]
			data.update({'list_i':new_i})
		else:
			state_l = state.list(self.update,self.context)
			data.update({'list':state_l,'list_i':state.list_start})
		if self._bkup_state_routes:
			self.conversation.add_routes(self.curr_state,self._bkup_state_routes)
			self._bkup_state_routes = None

	def _build_dynamic_routes(self,state):
		'''Build dynamic routes for current state'''
		ro,de,ba = state.routes(self.update,self.context)
		self.conversation.add_routes(state,ro,de,ba)

	def _build_dynamic_keyboard(self,state):
		'''Build dynamic keyboard for current state'''
		keyboard = state.build(self.update,self.context)
		keyboard,size = keyboard if isinstance(keyboard,tuple) else (keyboard,None)
		state.add_keyboard(keyboard,size,max_row=state.max_row)

	def _build_dynamic_list(self,state,keyboard):
		'''Build dynamic list for current state'''
		self._bkup_state_routes = self.conversation.routes.get(state.name)
		data = self.context.user_data.get(self.update.effective_chat.id)
		state_l = data.get('list')
		basic_routes = {k+len(state_l):v for k,v in self.conversation.routes.get(state.name).items()}
		for kl in keyboard:
			for button in kl: 
				if button.callback_data: button.callback_data += len(state_l)
		list_buttons = [InlineKeyboardButton(b,callback_data=i) for i,b in enumerate(state_l if state.list_all else state.list_buttons)]
		keyboard = [list_buttons]+keyboard
		self.list_keyboard = keyboard
		self.conversation.add_routes(state,basic_routes,default=state)
		if not state.list_all and (i := data.get('list_i')) in (0,len(state_l)-1):
			if len(state_l) < 2: keyboard.pop(0)
			else: keyboard[0].pop((1,0)[not i])
		if state.list_all and len(state_l) > 0: keyboard[data.get('list_i')//8].pop(data.get('list_i'))
		return keyboard

	def _build_dynamic_stuff(self,state): 
		'''Compute dynamic stuff: action > routes > keyboard > list'''
		data = self.context.user_data.get(self.update.effective_chat.id)
		if self.prev_state != self.curr_state and data.get('list'): data.pop('list'),data.pop('list_i')
		if state.list: self._update_dynamic_list(state)
		action_str = state.action(self.update,self.context) if state.action else None
		if state.routes: self._build_dynamic_routes(state)
		if state.build: self._build_dynamic_keyboard(state)
		keyboard = self._build_keyboard(state)
		if state.list: keyboard = self._build_dynamic_list(state,keyboard)
		reply_msg = state.msg if action_str == None else state.msg.replace('@@@',action_str)
		return InlineKeyboardMarkup(keyboard),reply_msg

	def restart(self):
		'''Restart handler to initial configuration'''
		if self.update:
			telegram_id = self.update.effective_chat.id
			if (c := self.context.user_data.get(telegram_id)):
				if (m := c.get('bot-msg')): m.delete()
				self.context.user_data.pop(telegram_id)
			self.prev_state = None
			self.curr_state = self.conversation.start
		return self

	def manage_conversation(self,update,context,delete_first=True):
		'''Master function for converastion'''
		self.update = update
		self.context = context
		telegram_id = self.update.effective_chat.id
		# start
		if not self.context.user_data.get(telegram_id):
			if delete_first: update.message.delete()
			state = self.conversation.start
			self.context.user_data.update({telegram_id:{'prev_state':None,'state':state.name,'error':False,'data':{}}})
			keyboard,reply_msg = self._build_dynamic_stuff(state)
			msg = self.update.message.reply_text(f'{reply_msg}',reply_markup=keyboard,parse_mode=state.mode)
			self.context.user_data.get(telegram_id).update({'bot-msg':msg})
			return self.NEXT
		# get data
		state = self.conversation.get_state(self.context.user_data.get(telegram_id).get('state'))
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
		if not self.conversation.routes.get(state.name) and state.routes: self._build_dynamic_routes(state)
		typed_data = state.data_type(data) if data != 'BACK' else 'BACK'
		state = self._change_state(telegram_id,typed_data)
		keyboard,reply_msg = self._build_dynamic_stuff(state)
		to_reply(f'{reply_msg}',reply_markup=keyboard,parse_mode=state.mode,disable_web_page_preview=not state.webpage_preview)
		if state == self.conversation.end: context.user_data.update({telegram_id:None}); return ConversationHandler.END
		return self.NEXT