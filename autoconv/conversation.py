from autoconv.state import State

def raise_type_error(var,name,types):
	if type(types) is not tuple: types = (types,)
	if var and not isinstance(var,types): raise TypeError(f"{name} must be {' or '.join([x.__name__ for x in types])}")

class Conversation:

	def __init__(self,start_state,end_state=None):
		self.start = start_state
		self.end = end_state
		self.state_list = [start_state,end_state] if end_state else [start_state]
		self.routes = {}

	def __str__(self):
		routes_print = '\n'.join(['  * {}:\n{}'.format(s,'\n'.join(['      {:>5} -> {}'.format(v,d) for v,d in r.items()])) for s,r in self.routes.items()])
		heading = f'CONVERSATION\n{self.start} ==> ' + (f'{self.end}' if self.end else f'...')
		return f'{heading}\n# State list: {[str(s) for s in self.state_list]}\n# Routes:\n{routes_print}'

	def _state_already_exists(self,state):
		'''Check for duplicates'''
		return any([state.name == s.name for s in self.state_list])

	def add_state(self,state):
		'''Add state to the conversation'''
		raise_type_error(state,'state',(State,list))
		for s in state:
			raise_type_error(s,'state',State)
			if not self._state_already_exists(s): self.state_list.append(s)
			else: raise ValueError(f'Already exists a state with name <{s.name}>.') 

	def add_routes(self,state,routes=None,default=None,back=None):
		'''Add state routes'''
		raise_type_error(state,'state',State)
		raise_type_error(routes,'routes',dict)
		raise_type_error(default,'default',State)
		raise_type_error(back,'back',State)
		if state not in self.state_list: raise ValueError(f'{state} doesn\'t exist in this conversation.')
		if routes:
			for k,v in routes.items():
				if (state.callback and k not in state.callback[0]) and k in (-1,'BACK'): raise ValueError(f'\'{k}\' it\'s not a possible value of {str(state)}.')
				if v not in self.state_list: raise ValueError(f'{str(v)} doesn\'t exist in this conversation.')
			self.routes.update({state.name:routes})
		if default:
			if default not in self.state_list: raise ValueError(f'{str(default)} doesn\'t exist in this conversation.')
			s.update({-1:default}) if (s := self.routes.get(state.name)) else self.routes.update({state.name:{-1:default}})
		if back:
			if back not in self.state_list: raise ValueError(f'{str(default)} doesn\'t exist in this conversation.')
			s.update({'BACK':back}) if (s := self.routes.get(state.name)) else self.routes.update({state.name:{'BACK':back}})