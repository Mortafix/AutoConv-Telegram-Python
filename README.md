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

# Documentation
I know you want examples, in fact there is a beautiful folder with some examples.  
But here, you can find a little documentation.

### State
```python
State(state_name:str,state_text:str,data_type:Callable=int,back_button:Optional[str]=None,**kwargs)
```
- `state_name`: state name (and key for data dictionary).
- `state_text`: message you want to print in that state.
- `data_type`: data type, default or custom.
- `back_button`: text for back button.
- `kwargs`: kwargs with every parameters you need from Telegram API _sendMessage_.

```python
# callback handler
add_keyboard(keyboard:Union[Sequence[str],Mapping[int,str]],size:Optional[Sequence[int]]=None,max_row:int=3)
```
- `keyboard`: inline keyboard. Can be a dict (with custom value as key) or a list/tuple (default int value as key).
- `size`: size for each row of the keyboard.
- `max_row`: max number of buttons in a row, ignored if size is specified.

```python
# text handler
add_text(regex:str=r'^.*$',error_message:Optional[str]=None)
```
- `regex`: regex for input text.
- `error_message`: error message when regex fails.

```python
# function to execute in this state
add_action(function:Callable)
```
- `function`: function must take one parameter (`TelegramData` object). It can return a `str`, repleacing 3 `@` (`@@@`) in the message. Called when its state is reached.

```python
# function to create dynamic keyboard
add_dynamic_keyboard(function:Callable,max_row:int=3)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a keyboard. Called when its state is reached.
- `max_row`: max number of buttons in a row.

```python
# function to create custom keyboard
add_custom_keyboard(function:Callable)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a list of _InlineKeyboardButton_. Called when its state is reached and it override the dynamic keyboard.

```python
# function to create dynamic routes
add_dynamic_routes(function:Callable)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a triplet (routes,default,back) [see _Conversation.add_routes()_ to better understanding]. Suggested to use in combo with _dynamic_keyboard_. Called when its state is reached.

```python
# function to create dynamic list
add_dynamic_list(function:Callable,start:int=0,left_button:str='<',right_button:str='>',all_elements:bool=False,max_row:int=4)
```
- `function`: function must take one parameter (`TelegramData` object). It must return a list of element. Called when its state is reached.
- `start`: starting position in the list.
- `left_button`,`right_button`: button labels to move in the list.
- `all_elements`: if you want to have all the elements in the list as buttons.
- `max_row`: max number of buttons in a row.

```python
# custom handler
add_custom_handler(handler:Callable,error_message:Optional[str]=None)
```
- `handler`: function must take one parameter (`TelegramData` object). It must return an hashable value used to get to next state (by routes) or None if the handler fails.
- `error_message`: error message when handler fails.

### Conversation
```python
Conversation(start_state:State,end_state:Optional[State]=None,fallback_state:Optional[State]=None)
```
- `start_state`: first state of the conversation.
- `end_state`: final state of the conversation.
- `fallback_state`: fallback handler state of the conversation (if defined, the conversation handle an error in this state).

```python
# define the routes for a state in the conversation (automatically added to conversation)
add_routes(state:State,routes:Optional[dict]=None,default:Optional[State]=None,back:Optional[State]=None)
```
- `state`: initial state of the ruote.
- `routes`: routes where a state should go for every possibile data received.
- `default`: default route if value isn't in ruotes.
- `back`: route to go when the back button is pressed, if exists.

```python
# get a states by name in the conversation
get_state(state_name:str)
```
- `state_name`: a state name to search in the conversation.

### AutoConvHandler
```python
AutoConvHandler(conversation:Conversation,telegram_state_name:Any)
```
- `conversation`: conversation to handle.
- `telegram_state_name`: Telegram state name to handle callback, text and other things.

```python
# manage conversation with update and context
manage_conversation(update:Telegram.Update,context:Telegram.Context,delete_first:bool=True)
```
- `update`,`context`: from telegram bot function.
- `delete_first`: if you want to delete the user message that trigger this handler.

```python
# restart the conversation to initial configuration
restart()
```

```python
# force a state in the conversation
force_state(state:Union[State,str])
```
- `state`: force the conversation to a specific state.

### TelegramData Attributes
- `update`,`context`: Telegram update and context.
- `telegram_id`: Telegram ID of the user.
- `user_data`: `context.user_data` of the user.
- `states_data`: data for every state of the user.
- `message`: message info, if possibile, of the user.
- `exception`: last Python exception occurred.
