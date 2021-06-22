from typing import Callable, Optional, Sequence, Union

from autoconv.state import State
from pydantic import validate_arguments


class Conversation:
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(
        self,
        start_state: State,
        end_state: Optional[State] = None,
        fallback_state: Optional[State] = None,
    ):
        self.start = start_state
        self.end = end_state
        self.fallback_state = fallback_state
        self.state_list = [st for st in [start_state, end_state, fallback_state] if st]
        self.routes = dict()
        self.users_list = None
        self.defaults = dict()
        self.default_func = str
        self.default_back = None

    def __str__(self):
        routes_print = "\n".join(
            [
                "  * {}:\n{}".format(
                    s,
                    "\n".join(["      {:>5} -> {}".format(v, d) for v, d in r.items()]),
                )
                for s, r in self.routes.items()
            ]
        )
        heading = f"CONVERSATION\n{self.start} ==> " + (
            f"{self.end}" if self.end else "..."
        )
        return (
            f"{heading}\n"
            f"# State list: {[str(s) for s in self.state_list]}\n"
            f"# Routes:\n{routes_print}"
        )

    def _add_states(self, states: Union[Sequence[State], State]):
        """Add states to the conversation"""
        if isinstance(states, State):
            states = (states,)
        for s in states:
            if s not in self.state_list:
                self.state_list.append(s)
            else:
                raise ValueError(f"Already exists a state with name <{s.name}>.")

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def add_routes(
        self,
        state: State,
        routes: Optional[dict] = None,
        default: Optional[State] = None,
        back: Optional[Union[bool, State]] = None,
    ):
        """Add routes for a state"""
        if state not in self.state_list:
            self._add_states(state)
        if self.routes.get(state.name):
            self.routes.pop(state.name)
        if routes:
            for k, v in routes.items():
                if (state.callback and k not in state.callback[0]) and k in (
                    -1,
                    "BACK",
                ):
                    raise ValueError(
                        f"'{k}' it's not a possible value of {str(state)}."
                    )
                if v not in self.state_list:
                    self._add_states(v)
            self.routes.update({state.name: routes})
        if default:
            if default not in self.state_list:
                self._add_states(default)
            s.update({-1: default}) if (
                s := self.routes.get(state.name)
            ) else self.routes.update({state.name: {-1: default}})
        if back or state.back_button or self.default_back:
            if not back and (
                state.back_button
                or (state.back_button is not False and self.default_back)
            ):
                back = True
            if isinstance(back, State) and back not in self.state_list:
                self._add_states(back)
            s.update({"BACK": back}) if (
                s := self.routes.get(state.name)
            ) else self.routes.update({state.name: {"BACK": back}})

    @validate_arguments
    def get_state(self, state_name: Optional[str]):
        """Get state from states list by name"""
        if state_name == self.start.name:
            return self.start
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
        self._add_states(no_auth_state)

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
