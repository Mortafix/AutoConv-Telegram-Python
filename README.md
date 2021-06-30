![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram-autoconv)
[![PyPI](https://img.shields.io/pypi/v/telegram-autoconv?color=red)](https://pypi.org/project/telegram-autoconv/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/mortafix/autoconv-telegram-python)

# Setup
You can find the package on PyPi (pip), [here](https://pypi.org/project/telegram-autoconv/).
```
pip3 install telegram-autoconv
```

# Requirements
* [Python 3.9+](https://www.python.org)
* [python-telegram-bot 13+](https://github.com/python-telegram-bot/python-telegram-bot)

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

# Examples
I know you want examples, in fact there is a beautiful folder with some [examples](https://github.com/Mortafix/AutoConv-Telegram-Python/tree/master/examples).  
In the table below, you can find an example for every functions in the module.
Function | Example
| :------------- | :----------
`add_keybord` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py)
`add_text` | [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py)
`add_action` | [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py)
`add_dynamic_keybord` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py)
`add_custom_keyboard` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py)
`add_dynamic_routes` | [keyboards.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/keyboards.py)
`add_dynamic_list` | [dynamic_list.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/dynamic_list.py)
`add_custom_handler`| [handlers.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/handlers.py)
`set_long_task`| [actions.py](https://github.com/Mortafix/AutoConv-Telegram-Python/blob/master/examples/actions.py)


# Documentation
Do you want to read? I got you cover, baby!  
No more than a little documentation in the [Wiki](https://github.com/Mortafix/AutoConv-Telegram-Python/wiki).
