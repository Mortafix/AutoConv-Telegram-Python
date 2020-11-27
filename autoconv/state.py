from math import ceil
from typing import Callable

def raise_type_error(var,name,types):
	if type(types) is not tuple: types = (types,)
	if var and not isinstance(var,types): raise TypeError(f"{name} must be {' or '.join([x.__name__ for x in types])}")

class State:

	def __init__(self,name,msg,type=int,parse_mode=None,back=False,webpage_preview=False):
		self.name = name
		self.data_type = type
		self.msg = msg
		self.mode = parse_mode
		self.callback = None
		self.text = None
		self.action = None
		self.build = None
		self.back = back
		self.webpage_preview = webpage_preview
		self.routes = None
	
	def __str__(self):
		return f'State <{self.name}>'

	def add_keyboard(self,keyboard,size=None,max_row=3):
		'''Add inline keyboard for the state'''
		raise_type_error(keyboard,'keyboard',(list,dict))
		raise_type_error(size,'size',tuple)
		if isinstance(keyboard,list): keyboard = dict(enumerate(keyboard))
		if size and sum(size) != len(keyboard): raise ValueError(f'Keyboard length ({len(keyboard)}) must be the same size as the sum of row size ({sum(size)}).')
		elem_n = len(keyboard)
		if not size: size = [max_row for _ in range(elem_n//max_row)] + ([r,] if (r := elem_n % max_row) else [])
		self.callback = (keyboard,tuple(size))

	def add_text(self,regex=None,error=None):
		'''Add handler for text input'''
		raise_type_error(regex,'regex',str)
		raise_type_error(error,'error',str)
		if not regex: regex = r'^.*$' 
		self.text = (regex,error)

	def add_action(self,function):
		'''Add action to do with this command'''
		raise_type_error(function,'function',(Callable))
		self.action = function

	def add_dynamic_keyboard(self,function,max_row=3):
		'''Add action to build a keyboard dynamically'''
		raise_type_error(function,'function',(Callable))
		raise_type_error(max_row,'max_row',(int))
		self.build = function
		self.max_row = max_row

	def add_dynamic_routes(self,function):
		'''Add function to create dynamic routes | must return 3 value (routes,default,back)'''
		raise_type_error(function,'function',(Callable))
		self.routes = function
