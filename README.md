# Setup

```
pip3 install telegram-autoconv
```

# Documentation
I know you want examples, in fact there is a beautiful folder with some examples.  
But here, you can find a little documentation.

### Status
```python
Status(name,message,type=int,parse_mode=None)
```
- `name`: Status name (and key for data dictionary). {`str`}
- `message`: message you want to print in that status. {`str`}
- `type`: data type. {`type`}
- `parse_mode`: Telegram message parse mode. {`Telegram.parse_mode`}

```python
# callback handler
add_keyboard(keyboard,size=None)
```
- `keyboard`: inline keyboard. Can be a dict (with custom value as key) or a list (default int value as key). {`name list` or `value:name dict`}
- `size`: size for each row of the keyboard. {`int tuple`}

```python
# text handler
add_text(regex=None,error_message=None)
```
- `regex`: regex for input text. {`str`}
- `error_message`: error message when regex fails. {`str`}

```python
# function to execute in this status
add_action(function)
```
- `function`: function must have two parameters (`update` and `context`). It can return a `str`, repleacing 3 `@` (`@@@`) in the message. {`func`}

### Conversation
```python
Conversation(start_status,end_status=None)
```
- `start_status`: first Status of the conversation. {`Status`}
- `end_status`: if exists, final Status of the conversation. {`Status`}

```python
# add status to the conversation
add_status(Status)
```
- `Status`: Add a Status or a list of Status to the conversation. {`Status` or `Status list`}

```python
# add status to the conversation
add_route(status,ruotes=None,default=None,back=None)
```
- `status`: initial Status of the ruote. {`Status`}
- `routes`: routes where a status should go for every possibile data received. {`value:Status dict`}
- `default`: default route if value isn't in ruotes. {`Status`}
- `back`: route to go when the back button is pressed. {`Status`}

### AutoConvHandler
```python
AutoConvHandler(conversation,telegram_state,back_button=False)
```
- `conversation`: conversation to handle. {`Conversation`}
- `telegram_state`: Telegram state name to handle callback, text and other things. {`Telegram.handler`}
- `back_button`: default back button for every Status. {`bool`}

```python
# manage conversation with update and context
manage_conversation(update,context)
```
- `update` e `context`: update and context from the telegram bot function. {`Telegram.update` and `Telegram.context`}
