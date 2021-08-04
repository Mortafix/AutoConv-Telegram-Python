![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram-autoconv)
[![PyPI](https://img.shields.io/pypi/v/telegram-autoconv?color=red)](https://pypi.org/project/telegram-autoconv/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/mortafix/autoconv-telegram-python)

![Alt text](images/Autoconv-Text.jpg "Autoconv")
Welcome to Autoconv!  
A Python package that help you build complex Telegram bot conversations with buttons, actions and much more.

# Setup
You can find the package on [PyPi (pip)](https://pypi.org/project/telegram-autoconv/).
```
pip3 install telegram-autoconv
```

### Requirements
* [Python 3.9+](https://www.python.org)
* [python-telegram-bot 13+](https://github.com/python-telegram-bot/python-telegram-bot)

# Examples
I know you want examples, in fact there is a beautiful folder with some [examples](https://github.com/Mortafix/AutoConv-Telegram-Python/tree/master/examples).  
In the table below, you can find an example for every functions in the module.  
In addition to that, there is a live Telegram bot to showcase every features, [@AutoBot](https://t.me/autoconv_bot).
Function | Example | Documentation
| :------------- | :---------- | :----------
`add_keybord` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-keyboard)
`add_text` | [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-text)
`add_dynamic_text` | [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-dynamic-text)
`add_action` | [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-action)
`add_dynamic_keybord` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-dynamic-keyboard)
`add_custom_keyboard` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-custom-keyboard)
`add_dynamic_routes` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-dynamic-routes)
`add_dynamic_list` | [dynamic_list.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/dynamic_list.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-dynamic-list)
`add_custom_handler`| [handlers.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/handlers.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-custom-handler)
`set_long_task`| [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#set-long-task)
`add_refresh_auth`| [authorization.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/authorization.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-refresh-auth)
`add_operation_buttons` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py) | [State](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/State#add-operation-buttons)
`Conversation` | [conversation.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/conversation.py) | [Conversation](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/Conversation#doc)
`add_routes` | [conversation.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/conversation.py) | [Conversation](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/Conversation#add-routes)
`set_defaults` | [defaults.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/defaults.py) | [Conversation](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/Conversation#set-defaults)
`add_authorized_users` | [authorization.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/authorization.py) | [Conversation](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/Conversation#add-authorized-users)
`state_messages` | [texts.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/texts.py) | [Texts Guide](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/Texts-Guide)
`set_timed_function` | [async.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/async.py) | [AutoConvHandler](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/AutoConv-Handler#set-timed-function)
`stop_timed_function` | [async.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/async.py) | [AutoConvHandler](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/AutoConv-Handler#stop-timed-function)
`send_autodestroy_message` | [async.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/async.py) | [AutoConvHandler](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/AutoConv-Handler#send-autodestroy-message)
`restart` | [autoconv_handler.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/autoconv_handler.py) | [AutoConvHandler](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/AutoConv-Handler#restart)
`force_state` | [autoconv_handler.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/autoconv_handler.py) | [AutoConvHandler](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki/AutoConv-Handler#force-state)

# Persistence
If you want to use persistence in your bot, Autoconv provides a simple persistence based on PicklePersistence.  
The normal PicklePersistence doesn't work, due to an instance of a `Telegram.Message` in the `user_data`, this persistence uses a workaround.
```python
from autoconv.utils.persistence import AutoconvPersistence
persistence = AutoconvPersistence(filename="bot_persistence", bot_token=BOT_TOKEN)
updater = Updater(BOT_TOKEN, persistence=persistence)
```
> WARNING! This persistence will save the bot token in a pickle file.

# Documentation
Do you want to read? I got you cover, baby!  
No more than a little documentation in the [Wiki](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki).

# Real World Example
I have a simple movies info Telegram bot publicy available.  
You can interact with the Bot (the response time it kinda high, caused by very slow connection) [PopCorn](https://t.me/poppycorn_bot) (sorry for the italian).  
The code (except for the config files) is in this [GIST](https://gist.github.com/Mortafix/93a866c71040557c309f0115aa1a2767).
