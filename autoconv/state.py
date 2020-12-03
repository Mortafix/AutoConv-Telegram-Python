from typing import Union,Callable,Optional,_GenericAlias,_VariadicGenericAlias

def type_check(func):
	def wrapper(*args,**kwargs):
		args_list = [(args[i+1],v,t) if i+1 < len(args) else (kwargs.get(v),v,t) for i,(v,t) in enumerate(func.__annotations__.items())]
		for a,v,t in args_list:
			if (isinstance(t,_VariadicGenericAlias) and not isinstance(a,t)) or (isinstance(t,_GenericAlias) and t.__args__ and not isinstance(a,t.__args__)) or (not isinstance(t,(_GenericAlias,_VariadicGenericAlias)) and not isinstance(a,t)):
				raise TypeError(f"{v} must be {(not isinstance(t,_GenericAlias) and t) or (t.__args__ and ' or '.join(x.__name__ for x in t.__args__)) or 'function'}")
		return func(*args,**kwargs)
	return wrapper

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
		self.custom = None
	
	def __str__(self):
		return f'State <{self.name}>'

	@type_check
	def add_keyboard(self,keyboard:Union[list,dict],size:Optional[tuple]=None,max_row:Optional[int]=3):
		'''Add inline keyboard for the state'''
		if isinstance(keyboard,list): keyboard = dict(enumerate(keyboard))
		if size and sum(size) != len(keyboard): raise ValueError(f'Keyboard length ({len(keyboard)}) must be the same size as the sum of row size ({sum(size)}).')
		elem_n = len(keyboard)
		if not size: size = [max_row for _ in range(elem_n//max_row)] + ([r,] if (r := elem_n % max_row) else [])
		self.callback = (keyboard,tuple(size))

	@type_check
	def add_text(self,regex:Optional[str]=None,error:Optional[str]=None):
		'''Add handler for text input'''
		if not regex: regex = r'^.*$' 
		self.text = (regex,error)

	@type_check
	def add_action(self,function:Callable):
		'''Add action to do with this command'''
		self.action = function

	@type_check
	def add_dynamic_keyboard(self,function:Callable,max_row:Optional[int]=3):
		'''Add action to build a keyboard dynamically'''
		self.build = function
		self.max_row = max_row

	@type_check
	def add_custom_keyboard(self,function:Callable):
		'''Add function to build custom ReplyMarkup keyboard | must return a value for ReplyMarkup'''
		self.custom = function

	@type_check
	def add_dynamic_routes(self,function):
		'''Add function to create dynamic routes | must return 3 value (routes,default,back)'''
		self.routes = function
