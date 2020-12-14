from autoconv.state import State
from typing import Union,Optional,Sequence
from pydantic import validate_arguments

class Conversation:

	@validate_arguments(config=dict(arbitrary_types_allowed=True))
	def __init__(self,start_state:State,end_state:Optional[State]=None,fallback_state:Optional[State]=None):
		self.start = start_state
		self.end = end_state
		self.fallback_state = fallback_state
		self.state_list = [st for st in [start_state,end_state,fallback_state] if st]
		self.routes = {}

	def __str__(self):
		routes_print = '\n'.join(['  * {}:\n{}'.format(s,'\n'.join(['      {:>5} -> {}'.format(v,d) for v,d in r.items()])) for s,r in self.routes.items()])
		heading = f'CONVERSATION\n{self.start} ==> ' + (f'{self.end}' if self.end else f'...')
		return f'{heading}\n# State list: {[str(s) for s in self.state_list]}\n#\tRoutes:\n{routes_print}'

	def _add_states(self,states:Union[Sequence[State],State]):
		'''Add states to the conversation'''
		if isinstance(states,State): states = (states,)
		for s in states:
			if s not in self.state_list: self.state_list.append(s)
			else: raise ValueError(f'Already exists a state with name <{s.name}>.') 

	@validate_arguments(config=dict(arbitrary_types_allowed=True))
	def add_routes(self,state:State,routes:Optional[dict]=None,default:Optional[State]=None,back:Optional[State]=None):
		'''Add routes for a state'''
		if state not in self.state_list: self._add_states(state)
		if self.routes.get(state.name): self.routes.pop(state.name)
		if routes:
			for k,v in routes.items():
				if (state.callback and k not in state.callback[0]) and k in (-1,'BACK'): raise ValueError(f'\'{k}\' it\'s not a possible value of {str(state)}.')
				if v not in self.state_list: self._add_states(v)
			self.routes.update({state.name:routes})
		if default:
			if default not in self.state_list: self._add_states(default)
			s.update({-1:default}) if (s := self.routes.get(state.name)) else self.routes.update({state.name:{-1:default}})
		if back:
			if back not in self.state_list: self._add_states(back)
			s.update({'BACK':back}) if (s := self.routes.get(state.name)) else self.routes.update({state.name:{'BACK':back}})

	@validate_arguments
	def get_state(self,state_name:str):
		'''Get state from states list by name'''
		if state_name == self.start.name: return self.start
		for state in self.state_list:
			if state.name == state_name: return state
		return None
