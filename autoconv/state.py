from functools import reduce
from typing import Callable, Mapping, Optional, Sequence, Union

from pydantic import validate_arguments


class State:
    @validate_arguments
    def __init__(
        self,
        state_name: str,
        state_text: str = "@@@",
        data_type: Callable = int,
        back_button: Optional[Union[bool, str]] = None,
        **kwargs,
    ):
        self.name = state_name
        self.msg = state_text
        self.data_type = data_type
        self.back_button = back_button
        self.kwargs = kwargs
        self.callback = None
        self.regex, self.regex_error_text = None, None
        self.action = None
        self.build, self.max_row = None, None
        self.custom = None
        self.routes = None
        self.list = None
        self.list_all = None
        self.list_buttons = None
        self.list_start = None
        self.list_max_row = None
        self.list_labels = None
        self.list_preserve = None
        self.handler, self.handler_error_text = None, None
        self.long_task = None
        self.refresh_auth = None
        self.operations = None
        self.dynamic_text = None

    def __str__(self):
        return f"State <{self.name}>"

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.name == other.name

    @validate_arguments
    def add_keyboard(
        self,
        keyboard: Union[Sequence[str], Mapping[int, str]],
        size: Optional[Sequence[int]] = None,
        max_row: int = 3,
    ):
        """Add inline keyboard handler"""
        if isinstance(keyboard, list):
            keyboard = dict(enumerate(keyboard))
        if size and sum(size) != len(keyboard):
            raise ValueError(
                f"Keyboard length ({len(keyboard)}) must be "
                "the same size as the sum of row size ({sum(size)})."
            )
        if size:
            size = reduce(
                lambda x, y: x + y,
                map(
                    lambda x: [x]
                    if x < 9
                    else [8] * (x // 8) + ([x % 8], [])[not x % 8],
                    size,
                ),
            )
        elem_n = len(keyboard)
        if not size:
            size = [max_row for _ in range(elem_n // max_row)] + (
                [r] if (r := elem_n % max_row) else []
            )
        self.callback = (keyboard, tuple(size))

    @validate_arguments
    def add_text(self, regex: str = r"^.*$", error_message: Optional[str] = None):
        """Add text input handler"""
        self.regex = regex
        self.regex_error_text = error_message

    @validate_arguments
    def add_dynamic_text(self, function: Callable):
        """Add function to build dynamic text regex
        must return 2 values (regex, message), both can be None"""
        self.dynamic_text = function

    @validate_arguments
    def add_action(self, function: Callable):
        """Add dynamic action"""
        self.action = function

    @validate_arguments
    def add_dynamic_keyboard(self, function: Callable, max_row: int = 3):
        """Add function to build a keyboard dynamically"""
        self.build = function
        self.max_row = max_row

    @validate_arguments
    def add_custom_keyboard(self, function: Callable):
        """Add function to build a custom keyboard
        must return a list of InlineKeyboardButton"""
        self.custom = function

    @validate_arguments
    def add_dynamic_routes(self, function: Callable):
        """Add function to create dynamic routes
        must return 3 value (routes,default,back)"""
        self.routes = function

    @validate_arguments
    def add_dynamic_list(
        self,
        function: Callable,
        start: int = 0,
        left_button: str = "<",
        right_button: str = ">",
        all_elements: bool = False,
        labels: Optional[Callable] = None,
        max_row: int = 4,
        preserve_index: bool = False,
    ):
        """Add function to create a dynamic list with pages"""
        self.list = function
        self.list_buttons = [left_button, right_button]
        self.list_all = all_elements
        self.list_start = start
        self.list_max_row = max_row
        self.list_labels = labels
        self.list_preserve = preserve_index

    @validate_arguments
    def add_custom_handler(
        self, handler: Callable, error_message: Optional[str] = None
    ):
        """Add function handler to handle a non-text message
        must return an hashable value used to get to next state (by routes)"""
        self.handler = handler
        self.handler_error_text = error_message

    @validate_arguments
    def set_long_task(self, text: str):
        """Add a middle message waiting for the long main task"""
        self.long_task = text

    @validate_arguments
    def add_refresh_auth(self, func: Callable):
        """Add function that return a new list of authorized users (Telegram ids)"""
        self.refresh_auth = func

    @validate_arguments
    def add_operation_buttons(
        self, operations: Union[Sequence[Callable], Mapping[int, Callable]]
    ):
        """Add functions for keyboard buttons, State is not changed"""
        if not isinstance(operations, Mapping):
            operations = {i: op for i, op in enumerate(operations)}
        self.operations = operations
