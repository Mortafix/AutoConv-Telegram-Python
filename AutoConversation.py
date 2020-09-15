from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from re import match
from math import ceil

def raise_type_error(var,name,types):
	if type(types) is not list: types = [types]
	if var and type(var) not in types: raise TypeError(f"{name} must be {' or '.join([x.__name__ for x in types])}")

class Status:

	def __init__(self,name,msg,type=int,parse_mode=None):
		self.name = name
		self.data_type = type
		self.msg = msg
		self.callback = None
		self.text = None
		self.action = None
		self.mode = parse_mode
	
	def __str__(self):
		return f'Status <{self.name}>'

	def add_keyboard(self,keyboard,size=None):
		'''Add inline keyboard for the status'''
		raise_type_error(keyboard,'keyboard',[list,dict])
		raise_type_error(size,'size',tuple)
		if type(keyboard) is list: keyboard = {i:v for i,v in enumerate(keyboard)}
		if size and sum(size) != len(keyboard): raise ValueError(f'Keyboard length ({len(keyboard)}) must be the same size as the sum of row size ({sum(size)}).')
		elem_n = len(keyboard)
		if not size: size = [3 for _ in range(elem_n//3)] + ([r,] if (r := elem_n % 3) else [])
		self.callback = (keyboard,tuple(size))

	def add_text(self,regex=None,error=None):
		'''Add handler for text input'''
		raise_type_error(regex,'regex',str)
		raise_type_error(error,'error',str)
		if not regex: regex = r'^.*$' 
		self.text = (regex,error)

	def add_action(self,function):
		'''Add action to do with this command'''
		self.action = function

class Conversation:

	def __init__(self,start_status,end_status=None):
		self.start = start_status
		self.end = end_status
		self.status_list = [start_status,end_status] if end_status else [start_status]
		self.routes = {}

	def __str__(self):
		routes_print = '\n'.join(['  * {}:\n{}'.format(s,'\n'.join(['      {:>5} -> {}'.format(v,d) for v,d in r.items()])) for s,r in self.routes.items()])
		heading = f'CONVERSATION\n{self.start} ==> ' + (f'{self.end}' if self.end else f'...')
		return f'{heading}\n# Status list: {[str(s) for s in self.status_list]}\n# Routes:\n{routes_print}'

	def _status_already_exists(self,status):
		'''Check for duplicates'''
		return any([status.name == s.name for s in self.status_list])

	def add_status(self,status):
		'''Add status to the conversation'''
		raise_type_error(status,'status',[Status,list])
		for s in status:
			raise_type_error(s,'status',Status)
			if not self._status_already_exists(s): self.status_list.append(s)
			else: raise ValueError(f'Already exists a status with name <{s.name}>.') 

	def add_routes(self,status,routes=None,default=None,back=None):
		'''Add status routes'''
		raise_type_error(status,'status',Status)
		raise_type_error(routes,'routes',dict)
		raise_type_error(default,'default',Status)
		raise_type_error(back,'back',Status)
		if status not in self.status_list: raise ValueError(f'{status} does not exists in this conversation.')
		if routes:
			for k,v in routes.items():
				if (status.callback and k not in status.callback[0]) and k in (-1,'BACK'): raise ValueError(f'\'{k}\' it\'s not a possible value of {str(status)}.')
				if v not in self.status_list: raise ValueError(f'{str(v)} does not exists in this conversation.')
			self.routes.update({status.name:routes})
		if default:
			if default not in self.status_list: raise ValueError(f'{str(default)} does not exists in this conversation.')
			s.update({-1:default}) if (s := self.routes.get(status.name)) else self.routes.update({status.name:{-1:default}})
		if back:
			if back not in self.status_list: raise ValueError(f'{str(default)} does not exists in this conversation.')
			s.update({'BACK':back}) if (s := self.routes.get(status.name)) else self.routes.update({status.name:{'BACK':back}})

class AutoConvHandler:

	def __init__(self,conversation,telegram_state_name,back_button=False):
		self.conversation = conversation
		self.NEXT = telegram_state_name
		self.back = back_button

	def _build_keyboard(self,status):
		'''Build Keyboard for callback status'''
		cmd_list = [[InlineKeyboardButton(text=key_param[0][i+su],callback_data=i+su) for i in range(si)] for si,su in zip(key_param[1],[sum(key_param[1][:i]) for i in range(len(key_param[1]))])] if (key_param := status.callback) else [[]]
		if self.back and status not in (self.conversation.start,self.conversation.end): cmd_list += [[InlineKeyboardButton(text='Indietro',callback_data='BACK')]]
		return InlineKeyboardMarkup(cmd_list) 

	def _next_status(self,status,value):
		'''Follow status ruote'''
		if value not in self.conversation.routes.get(status.name) and -1 not in self.conversation.routes.get(status.name): raise ValueError(f'Value {value} don\'t exists as route of {status}, neither a default route.') 
		return self.conversation.routes.get(status.name).get(value) if value in self.conversation.routes.get(status.name) else self.conversation.routes.get(status.name).get(-1)

	def _change_status(self,telegram_id,data):
		'''Set variables for next status'''
		status = self.context.user_data.get(telegram_id).get('status')
		value = status.callback[0][data] if status.callback and status.callback[0].get(data) else data
		if status != self.conversation.end: self.context.user_data.get(telegram_id).get('data').update({status.name:value})
		new_status = self._next_status(status,data)
		self.context.user_data.get(telegram_id).update({'status':new_status,'error':False})
		return new_status

	def _wrong_text(self):
		'''Handler for wrong regex in text status'''
		telegram_id = self.update.message.chat.id
		self.update.message.delete()
		status = self.context.user_data.get(telegram_id).get('status')
		if status.text and not self.context.user_data.get(telegram_id).get('error'):
			keyboard = self._build_keyboard(status)
			self.context.user_data.get(telegram_id).update({'error':True})
			self.context.user_data.get(telegram_id).get('bot-msg').edit_text(f"{status.msg}\n\n{status.text[1]}",reply_markup=keyboard,parse_mode=status.mode)
		return self.NEXT

	def _going_back(self):
		'''Handler for back button'''
		query = self.update.callback_query
		telegram_id = self.update.callback_query.message.chat.id
		new_status = self._change_status(telegram_id,'BACK')
		keyboard = self._build_keyboard(new_status)
		query.edit_message_text(f"{new_status}",reply_markup=keyboard,parse_mode=new_status.mode)
		return self.NEXT

	def manage_conversation(self,update,context):
		'''Master function for converastion'''
		self.update = update
		self.context = context
		telegram_id = self.update.effective_chat.id
		# start
		if not self.context.user_data.get(telegram_id):
			status = self.conversation.start
			keyboard = self._build_keyboard(status)
			msg = self.update.message.reply_text(f'{status.msg}',reply_markup=keyboard,parse_mode=status.mode)
			self.context.user_data.update({telegram_id:{'status':status,'error':False,'bot-msg':msg,'data':{}}})
			return self.NEXT
		# get data
		status = self.context.user_data.get(telegram_id).get('status')
		if self.update.callback_query:
			data = self.update.callback_query.data
			to_reply = self.update.callback_query.edit_message_text
		else:
			data = self.update.message.text
			if not status.text: self.update.message.delete(); return self.NEXT
			if not match(status.text[0],data): return self._wrong_text()
			to_reply = self.context.user_data.get(telegram_id).get('bot-msg').edit_text
			self.update.message.delete()
		# next stage
		typed_data = status.data_type(data) if data != 'BACK' else 'BACK'
		status = self._change_status(telegram_id,typed_data)
		keyboard = self._build_keyboard(status)
		ret = status.action(self.update,self.context) if status.action else None
		msg = status.msg if ret == None else status.msg.replace('@@@',ret)
		to_reply(f'{msg}',reply_markup=keyboard,parse_mode=status.mode)
		if status == self.conversation.end: context.user_data.update({telegram_id:None}); return ConversationHandler.END
		return self.NEXT
