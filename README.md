![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram-autoconv)
[![PyPI](https://img.shields.io/pypi/v/telegram-autoconv?color=red)](https://pypi.org/project/telegram-autoconv/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/mortafix/autoconv-telegram-python)

# Setup
You can find the package, [here](https://pypi.org/project/telegram-autoconv/).
```
pip3 install telegram-autoconv
```

# Requirements
* Python 3.8
* telegram-python-bot 13

# Import
```python
from autoconv.state import State
from autoconv.conversation import Conversation
from autoconv.autoconv_handler import AutoConvHandler
```

# Persistence
If you want to use persistence in your bot, Autoconv provides a simple persistence based on PicklePersistence. The normal PicklePersistence doesn't work, due to an instance of a `Telegram.Message` in the `user_data`, this persistence uses a workaround.
```python
from autoconv.persistence import AutoconvPersistence
persistence = AutoconvPersistence(filename="bot_persistence", bot_token=BOT_TOKEN)
updater = Updater(BOT_TOKEN, persistence=persistence)
```
> WARNING! This persistence will save the bot token in a pickle file.

# Documentation
I know you want examples, in fact there is a beautiful folder with some [examples](https://github.com/Mortafix/AutoConv-Telegram-Python/tree/master/examples).
But here, you can find a little documentation.

### State
```python
State(
    state_name: str,
    state_text: str,
    data_type: Callable = int,
    back_button: Optional[Union[bool, str]] = None,
    **kwargs
)
```
- `state_name`: state name (and key for data dictionary).
- `state_text`: message you want to print in that state.
- `data_type`: data type, default or custom.
- `back_button`: text for back button. _False_ if you have a default button (defined in the Conversation) and you don't want it in this State.
- `kwargs`: kwargs with every parameters you need from Telegram API _sendMessage_.

```python
# callback handler
State.add_keyboard(
    keyboard: Union[Sequence[str],Mapping[int, str]],
    size: Optional[Sequence[int]] = None,
    max_row: int = 3
)
```
- `keyboard`: inline keyboard. Can be a dict (with custom value as key) or a list/tuple (default int value as key).
- `size`: size for each row of the keyboard.
- `max_row`: max number of buttons in a row, ignored if size is specified.

```python
# text handler
State.add_text(
    regex: str = r'^.*$',
    error_message: Optional[str] = None
)
```
- `regex`: regex for input text.
- `error_message`: error message when regex fails.

```python
# function to execute in this state
State.add_action(
    function: Callable
)
```
- `function`: function must take one parameter (`TelegramData` object). It can return a `str`, repleacing 3 `@` (`@@@`) in the message. Called when its state is reached.

```python
# function to create dynamic keyboard
State.add_dynamic_keyboard(
    function: Callable,
    max_row: int = 3
)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a keyboard. Called when its state is reached.
- `max_row`: max number of buttons in a row.

```python
# function to create custom keyboard
State.add_custom_keyboard(
    function: Callable
)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a list of _InlineKeyboardButton_. Called when its state is reached and it override the dynamic keyboard.

```python
# function to create dynamic routes
State.add_dynamic_routes(
    function: Callable
)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a triplet (routes,default,back) [see `Conversation.add_routes()` to better understanding]. Suggested to use in combo with _dynamic keyboard_. Called when its state is reached.

```python
# function to create dynamic list
State.add_dynamic_list(
    function: Callable,
    start: int = 0,
    left_button: str = '<',
    right_button: str = '>',
    all_elements: bool = False,
    labels: Optional[Callable] = None,
    max_row: int = 4
)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a list of element. Called when its state is reached.
- `start`: starting position in the list.
- `left_button`,`right_button`: button labels to move in the list.
- `all_elements`: if you want to have all the elements in the list as buttons.
- `max_row`: max number of buttons in a row.
- `labels`: function must take one parameter (`TelegramData` object). Combined with `all_elements = True`, it must return a list of string in order to change buttons labels. Called when its state is reached.

```python
# function to create a custom handler
State.add_custom_handler(
    handler: Callable,
    error_message: Optional[str] = None
)
```
- `handler`: function must take one parameter (`TelegramData` object). It must return an hashable value used to get to next state (by routes) or None if the handler fails.
- `error_message`: error message when handler fails.

```python
# function to set a long task
State.set_long_task(
    self, text: str
)
```
- `text`: text for a message that will be sent before the main one (for long task).

```python
# function that return a new list of authorized users
State.add_refresh_auth(
    self, func: Callable
)
```
- `func`: function must take one parameter (`TelegramData` object). It must return a list of Telegram ids. Called when its state is reached.

### Conversation
```python
Conversation(
    start_state: State,
    end_state: Optional[State] = None,
    fallback_state: Optional[State] = None
)
```
- `start_state`: first state of the conversation.
- `end_state`: final state of the conversation.
- `fallback_state`: fallback handler state of the conversation (if defined, the conversation handle an error in this state).

```python
# define the routes for a state in the conversation (automatically added to conversation)
Conversation.add_routes(
    state: State,
    routes: Optional[dict] = None,
    default: Optional[State] = None,
    back: Optional[State] = None
)
```
- `state`: initial state of the ruote.
- `routes`: routes where a state should go for every possibile data received.
- `default`: default route if value isn't in ruotes.
- `back`: route to go when the back button is pressed, if exists. If the state isn't specified and the starting state has a back button, it'll go to back the previous state.

```python
# get a states by name in the conversation
Conversation.get_state(
    state_name: str
)
```
- `state_name`: a state name to search in the conversation.

```python
# define a list of users able to access this conversation and an optional fallback State
Conversation.add_authorized_users(
    users_list: Sequence[int],
    no_auth_state: State
)
```
- `users_list`: list of users (Telegram ID) able to access the conversation.
- `no_auth_state`: state in which unauthorized users end up.

```python
# Define default values, a function applied to text and a back button for every States in the conversation
Conversation.set_defaults(
    params: Optional[dict] = None,
    func: Optional[Callable] = None,
    back_button: Optional[str] = None,
)
```
- `params`: kwargs with every parameters you need from Telegram API _sendMessage_.
- `function`: default function applied to every State text.
- `back_button`: default back button for every State.

### AutoConvHandler
```python
AutoConvHandler(
    conversation: Conversation,
    telegram_state_name: Any
)
```
- `conversation`: conversation to handle.
- `telegram_state_name`: Telegram state name to handle callback, text and other things.

```python
# manage conversation with update and context
AutoConvHandler.manage_conversation(
    update: Telegram.Update,
    context: Telegram.Context,
    delete_first: bool = True
)
```
- `update`,`context`: from telegram bot function.
- `delete_first`: if you want to delete the user message that trigger this handler.

```python
# restart the conversation to initial configuration
AutoConvHandler.restart(
    update: Telegram.Update,
    context: Telegram.Context
)
```
- `update`,`context`: from telegram bot function.

```python
# force a state in the conversation
AutoConvHandler.force_state(
    state: Union[State, str],
    update: Telegram.Update
)
```
- `state`: force the conversation to a specific state.
- `update`: from telegram bot function.

### TelegramData Attributes
- `update`,`context`: Telegram update and context.
- `telegram_id`: Telegram ID of the user.
- `udata`: `context.user_data` of the user.
- `sdata`: data for every state of the user.
- `message`: message info, if possibile, of the user.
- `exception`: last Python exception occurred.
- `users`: list of current authorized users.
