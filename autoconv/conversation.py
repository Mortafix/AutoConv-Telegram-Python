from json import load as jload
from re import search
from typing import Callable, Mapping, Optional, Sequence, Union
from warnings import warn

from autoconv.state import State
from pydantic import validate_arguments
from toml import load as tload
from yaml import load as yload


class Conversation:
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(
        self,
        start_state: State,
        end_state: Optional[State] = None,
        fallback_state: Optional[State] = None,
        state_messages: Optional[Union[str, Mapping[str, str]]] = None,
    ):
        self.start = start_state
        self.end = end_state
        self.fallback_state = fallback_state
        self.state_list = list()
        self.routes = dict()
        self.users_list = None
        self.defaults = dict()
        self.default_func = str
        self.default_back = None
        self.messages = state_messages
        self.add_routes(start_state)
        end_state and self.add_routes(end_state)
        fallback_state and self.add_routes(fallback_state)

    def __str__(self):
        """Pretty printing of conversation"""
        routes = [
            f"  * {st}:\n" + "\n".join([f"\t{va:>4} -> {ro}" for va, ro in rou.items()])
            for st, rou in sorted(self.routes.items())
        ]
        return "> CONVERSATION\n# Routes:\n" + "\n".join(routes)

    # ---- Dev

    def _add_state(self, state: State):
        """Add states to the conversation"""
        if state in self.state_list:
            raise ValueError(f"Already exists a state with name '{state.name}'.")
        self.state_list.append(state)

    def _check_routes(self):
        """Check if very state has the routes, if not raise a warning"""
        for state in self.state_list:
            if state.name not in self.routes and not state.routes:
                warn(f"No routes found for {state}")

    def _set_states_text(self):
        """Load states messages from a file or a dict"""
        if not self.messages:
            return
        if isinstance(self.messages, str):
            ops = {"yaml": yload, "json": jload, "toml": tload}
            extension = search(r"\.(\w+)$", self.messages).group(1)
            if extension not in ops:
                raise ValueError(f"File '.{extension}' not supported")
            self.messages = ops.get(extension)(open(self.messages, encoding="utf-8"))
            if not isinstance(self.messages, dict):
                raise TypeError("Texts loaded form file must be a dictionary")
        for state in self.state_list:
            state.msg = self.messages.get(state.name) or state.msg

    # ---- Public

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def add_routes(
        self,
        state: State,
        routes: Optional[Mapping[int, State]] = None,
        default: Optional[State] = None,
        back: Optional[Union[bool, State]] = None,
    ):
        """Add routes for a state"""
        if state not in self.state_list:
            self._add_state(state)
        if self.routes.get(state.name):
            self.routes.pop(state.name)
        routes_dict = dict()
        if routes:
            for k, v in routes.items():
                if state.callback and k not in state.callback[0] and k in (-1, "BACK"):
                    raise ValueError(f"'{k}' it's not a possible value of {state}.")
                if v not in self.state_list:
                    self._add_state(v)
            routes_dict.update(routes)
        if default:
            if default not in self.state_list:
                self._add_state(default)
            routes_dict.update({-1: default})
        if back or state.back_button or self.default_back:
            if not back and (
                state.back_button
                or (state.back_button is not False and self.default_back)
            ):
                back = True
            if isinstance(back, State) and back not in self.state_list:
                self._add_state(back)
            routes_dict.update({"BACK": back})
        self.routes.update({state.name: routes_dict})

    @validate_arguments
    def get_state(self, state_name: Optional[str]):
        """Get state from states list by name"""
        for state in self.state_list:
            if state.name == state_name:
                return state
        return None

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def add_authorized_users(
        self, users_list: Sequence[int], no_auth_state: Optional[State] = None
    ):
        """Define a list of users able to access this conversation"
        and an optional fallback State"""
        self.no_auth_state = no_auth_state
        self.users_list = users_list
        self.add_routes(no_auth_state)

    @validate_arguments
    def set_defaults(
        self,
        params: Optional[dict] = None,
        func: Optional[Callable] = None,
        back_button: Optional[str] = None,
    ):
        """Define default values, a function applied to text and a back button
        for every States in the conversation"""
        self.defaults = params
        self.default_func = func or str
        self.default_back = back_button
