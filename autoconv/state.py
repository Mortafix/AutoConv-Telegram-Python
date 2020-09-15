from math import ceil

def raise_type_error(var,name,types):
	if type(types) is not list: types = [types]
	if var and type(var) not in types: raise TypeError(f"{name} must be {' or '.join([x.__name__ for x in types])}")

class State:

	def __init__(self,name,msg,type=int,parse_mode=None):
		self.name = name
		self.data_type = type
		self.msg = msg
		self.callback = None
		self.text = None
		self.action = None
		self.mode = parse_mode
	
	def __str__(self):
		return f'State <{self.name}>'

	def add_keyboard(self,keyboard,size=None):
		'''Add inline keyboard for the state'''
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