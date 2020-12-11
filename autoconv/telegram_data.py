class TelegramData:

	def __init__(self):
		self.update = None
		self.context = None
		self.telegram_id = None
		self.user_data = None
		self.states_data = None
		self.message = None
		self.exception = None

	def __str__(self):
		return f"UPDATE {self.update}\nCONTEXT {self.context}\nTELEGRAM ID {self.telegram_id}\nUSER DATA {self.user_data}\nSTATES DATA {self.states_data}"

	def update_telegram_data(self,update,context):
		self.update = update
		self.context = context

	def prepare(self):
		self.telegram_id = self.update.effective_chat.id
		self.user_data = self.context.user_data.get(self.telegram_id)
		self.states_data = self.user_data.get('data') if self.user_data else None
		self.message = self.update.message
		return self