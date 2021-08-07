from copy import deepcopy
from datetime import datetime
from math import ceil
from re import match
from time import sleep

from autoconv.utils.telegram_data import TelegramData
from autoconv.utils.timed_thread import TimedThread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ConversationHandler


class AutoConvHandler:
    def __init__(self, conversation, telegram_state_name):
        self.conversation = conversation
        self.NEXT = telegram_state_name
        self.tData = TelegramData(self, conversation.users_list)
        self.prev_state = None
        self.curr_state = conversation.start
        self._bkup_routes, self._list_keyboard, self._bkup_indexes = None, None, dict()
        self.list_labels = None
        self.conversation._check_routes()
        self.conversation._set_states_text()
        self.threads = list()
        self.EXIT_SIGNAL = "!EXIT!"

    # -------- changing state --------

    def _build_keyboard(self, state):
        """Build Keyboard for callback state"""
        cmd_list = (
            [
                [
                    InlineKeyboardButton(text=key_param[0][k], callback_data=k)
                    for k in list(key_param[0].keys())[su : su + si]
                ]
                for si, su in zip(
                    key_param[1],
                    [sum(key_param[1][:i]) for i in range(len(key_param[1]))],
                )
            ]
            if (key_param := state.callback)
            else [[]]
        )
        back_button_text = state.back_button or self.conversation.default_back
        back_button = (
            [[InlineKeyboardButton(text=back_button_text, callback_data="BACK")]]
            if back_button_text and self.conversation.routes.get(state.name).get("BACK")
            else []
        )
        return (
            (state.custom and state.custom(self.tData.prepare())) or cmd_list
        ) + back_button

    def _next_state(self, state, value):
        """Follow state ruote"""
        states = self.conversation.routes.get(state.name)
        if value not in states and -1 not in states:
            raise ValueError(
                f"Deafult route not found and value {value} "
                f"doesn't exist as route of {state}."
            )
        if value == "BACK" and states.get(value) is True:
            return self.prev_state
        return states.get(value) or states.get(-1)

    def _change_state(self, data, state=None):
        """Set variables for next state"""
        data_context = self.tData.context.user_data
        if not state:
            state = self.conversation.get_state(
                self.tData.context.user_data.get("state")
            )
            if state.list and isinstance(data, int) and not self.tData.update.message:
                value = [
                    b for b in sum(self._list_keyboard, []) if b.callback_data == data
                ][0].text
            else:
                value = state.callback and state.callback[0].get(data) or data
            if state != self.conversation.end:
                self.tData.context.user_data.get("data").update({state.name: value})
            new_state = self._next_state(state, data)
        else:
            new_state = state
        self.prev_state, self.curr_state = self.curr_state, new_state
        data_context.update(
            {"prev_state": self.prev_state.name, "state": new_state.name}
        )
        if new_state.regex or new_state.handler:
            data_context.update({"error": False, "error-counter": 0})
        elif data_context.get("error") is not None:
            data_context.pop("error")
            data_context.pop("error-counter")
        self._restore_basic_routes()
        return new_state

    def _wrong_message(self, text, data):
        """Handler for wrong message"""
        self.tData.update.message.delete()
        state = self.conversation.get_state(self.tData.context.user_data.get("state"))
        self._restore_basic_routes()
        # save data
        error_counter = self.tData.context.user_data.get("error-counter", 0)
        error_values = {"error": True, "error-counter": error_counter + 1}
        self.tData.context.user_data.update(error_values)
        self.tData.context.user_data.get("data").update({state.name: data})
        # update msg
        error_text = text and state.regex_error_text or state.handler_error_text
        func = (
            lambda x: x + f"\n\n{error_text}"
            if error_text and not state.dynamic_text
            else x
        )
        self._send_message(
            state, self.tData.context.user_data.get("bot-msg").edit_text, post_func=func
        )
        return self.NEXT

    # -------- Dynamic stuff --------

    def _update_dynamic_list(self, state):
        """Update i and routes backup for dynamic list"""
        data = self.tData.context.user_data
        if (state_l := data.get("list")) :
            i = int(data.get("list_i"))
            new_i = i
            if state.list_all:
                curr_list = self.list_labels or state_l
                elem_list = data.get("data").get(state.name)
                new_i = curr_list.index(elem_list) if elem_list in curr_list else i
            elif data.get("data").get(state.name) in state.list_buttons:
                roads = {state.list_buttons[0]: i - 1, state.list_buttons[1]: i + 1}
                new_i = roads.get(data.get("data").get(state.name), i)
            elem = state_l[new_i]
            data.update({"list_i": new_i, "list_el": elem})
        else:
            state_l = state.list(self.tData.prepare())
            saved_i = self._bkup_indexes.get(state.name, state.list_start)
            elem = state_l[saved_i]
            data.update({"list": state_l, "list_i": saved_i, "list_el": elem})

    def _build_dynamic_list(self, state, keyboard):
        """Build dynamic list for current state"""
        if self.prev_state != self.curr_state:
            self._bkup_routes = (state.name, self.conversation.routes.get(state.name))
        data = self.tData.context.user_data
        state_l = data.get("list")
        basic_routes = {
            k + len(state_l): v
            for k, v in self.conversation.routes.get(state.name).items()
            if k not in ("BACK", -1)
        }
        for kl in keyboard:
            for button in kl:
                if (cd := button.callback_data) is not None and isinstance(cd, int):
                    button.callback_data += len(state_l)
        self.list_labels = state.list_labels and state.list_labels(self.tData.prepare())
        maxr, btns = state.list_max_row, state.list_buttons
        list_buttons = [
            [
                InlineKeyboardButton(
                    self.list_labels[r * maxr + i] if self.list_labels else button,
                    callback_data=r * maxr + i,
                )
                for i, button in enumerate(
                    state_l[r * maxr : r * maxr + maxr] if state.list_all else btns
                )
            ]
            for r in range(ceil((len(state_l) if state.list_all else 1) / maxr))
        ]
        keyboard = list_buttons + keyboard
        self._list_keyboard = keyboard
        self.conversation.add_routes(
            state,
            basic_routes,
            default=state,
            back=self.conversation.routes.get(state.name).get("BACK"),
        )
        if not state.list_all and (i := data.get("list_i")) in (0, len(state_l) - 1):
            if len(state_l) < 2:
                keyboard.pop(0)
            else:
                keyboard[0].pop((1, 0)[not i])
        if state.list_all and len(state_l) > 0:
            keyboard[data.get("list_i") // state.list_max_row].pop(
                data.get("list_i") % state.list_max_row
            )
        return keyboard

    def _build_dynamic_routes(self, state):
        """Build dynamic routes for current state"""
        routes, default, back = state.routes(self.tData.prepare())
        self.conversation.add_routes(state, routes, default, back)

    def _build_dynamic_keyboard(self, state):
        """Build dynamic keyboard for current state"""
        keyboard = state.build(self.tData.prepare())
        keyboard, size = keyboard if isinstance(keyboard, tuple) else (keyboard, None)
        state.add_keyboard(keyboard, size, max_row=state.max_row)

    def _refresh_auth_users(self, state):
        """Refresh authorized users"""
        new_users = state.refresh_auth(self.tData.prepare())
        self.conversation.users_list = new_users
        self.tData.users = new_users

    def _build_dynamic_text(self, state):
        regex, message = state.dynamic_text(self.tData.prepare())
        state.add_text(regex is None and r"^.*$" or regex, message)
        if self.tData.udata.get("error") and state.regex_error_text:
            return f"\n\n{state.regex_error_text}"
        return ""

    def _build_dynamic_stuff(self, state):
        """Compute dynamic stuff: action > text > routes > keyboard > list > refresh"""
        data = self.tData.context.user_data
        msg = state.msg
        if self.prev_state != self.curr_state and data.get("list"):
            data.pop("list")
            data.pop("list_el")
            last_i = data.pop("list_i")
            if not self.prev_state:
                self.prev_state = state
            if self.prev_state and self.prev_state.list_preserve:
                self._bkup_indexes.update({self.prev_state.name: last_i})
            self.list_labels, self._bkup_routes = None, None
        if state.list:
            self._update_dynamic_list(state)
        if state.action:
            action_str = state.action(self.tData.prepare())
            if action_str == self.EXIT_SIGNAL:
                return action_str
        if state.dynamic_text:
            msg += self._build_dynamic_text(state)
        if state.routes:
            self._build_dynamic_routes(state)
        if state.build:
            self._build_dynamic_keyboard(state)
        keyboard = self._build_keyboard(state)
        if state.list:
            keyboard = self._build_dynamic_list(state, keyboard)
        if state.refresh_auth:
            self._refresh_auth_users(state)
        reply_msg = msg.replace("@@@", state.action and str(action_str) or "")
        return InlineKeyboardMarkup(keyboard), reply_msg

    # -------- Dev functions --------

    def _restore_basic_routes(self):
        if not self._bkup_routes:
            return
        state, routes = deepcopy(self._bkup_routes)
        self.conversation.add_routes(
            self.conversation.get_state(state),
            routes,
            default=routes.pop(-1, None),
            back=routes.pop("BACK", None),
        )

    def _init_context(self, state):
        """Initializate user data in context"""
        if not self.tData.context.user_data:
            self.tData.context.user_data.update(
                {"prev_state": None, "state": state.name, "data": {}}
            )

    def _handle_bad_request(self, exception, update, state):
        """Handle every bad request"""
        self.tData.exception = exception
        if match("Message to edit not found", str(exception)):
            return self._send_message(state, update.message.reply_text)
        if not match("Message is not modified", str(exception)):
            if self.conversation.fallback_state:
                return self.force_state(self.conversation.fallback_state, update)
            raise exception

    def _send_message(self, state, send_func, elements=None, save=True, post_func=str):
        """Main function to send messages"""
        msg, keyboard = elements or (None, None)
        if state.long_task:
            send_func(state.long_task)
        if not elements:
            reply_dynamic = self._build_dynamic_stuff(state)
            if isinstance(reply_dynamic, str):
                if reply_dynamic == self.EXIT_SIGNAL:
                    return
            keyboard, msg = reply_dynamic
        new_msg = send_func(
            self.conversation.default_func(post_func(msg)),
            reply_markup=keyboard,
            **(self.conversation.defaults | state.kwargs),
        )
        self.tData.context.user_data.update({"last-message-time": str(datetime.now())})
        if save:
            self.tData.context.user_data.update({"bot-msg": new_msg})
        return new_msg

    def _do_operations(self, state, data):
        if isinstance(data, int):
            data = data - len(self.tData.udata.get("list", []))
        if state.operations and data in state.operations:
            return state.operations.get(data)(self.tData.prepare())
        return False

    # -------- Public functions ---------

    # ---- async
    def set_timed_function(self, seconds, state=None, function=None):
        """Start a timer to change the state"""
        self.stop_timed_function()

        def _timed_force_state():
            if function:
                function(self.tData.prepare())
            if state:
                self.force_state(state, self.tData.update)

        name = state and (isinstance(state, str) and state or state.name)
        name = name or function and function.__name__
        thread = TimedThread(seconds, name=name, target=_timed_force_state)
        self.threads.append(thread)
        thread.start()

    def stop_timed_function(self, state=None, function=None):
        """Stop a running thread, while cleaning dead thread"""
        name = state and (isinstance(state, str) and state or state.name)
        name = name or function and function.__name__
        for i, thread in enumerate(self.threads):
            if thread.name == name or thread.is_dead:
                thread.stop()
                self.threads.pop(i)

    def send_autodestroy_message(self, msg, seconds, **kwargs):
        """Send a message (outside the conversation) that will autodestroy itself"""

        def send_message(tdata):
            chat_id = tdata.update.effective_chat.id
            msg_id = tdata.context.bot.send_message(chat_id, msg, **kwargs)
            sleep(seconds)
            msg_id.delete()

        self.set_timed_function(0, function=send_message)

    def get_threads(self):
        """Get running threads, true=alive false=dead"""
        return {
            thread.name: thread.is_dead and "dead" or "running"
            for thread in self.threads
        }

    # ---- forcing
    def force_state(self, state, update):
        """Force a state in the conversation"""
        if isinstance(state, str):
            state = self.conversation.get_state(state)
        if state in self.conversation.state_list:
            # prepare data
            self._init_context(state)
            state = self._change_state(None, state=state)
            # check if the message exists
            old_msg = self.tData.context.user_data.get("bot-msg")
            send_msg = old_msg and old_msg.edit_text or update.message.reply_text
            try:
                self._send_message(state, send_msg)
            except BadRequest as e:
                self._handle_bad_request(e, update, state)
            return self.NEXT

    def restart(self, update, context):
        """Restart handler to initial configuration"""
        if self.tData.context:
            self.tData.context.user_data.get("data").clear()
            self.tData.context.user_data.pop("bot-msg")
            self.tData.prepare()
        else:
            self.tData.update_telegram_data(update, context)
        return self.force_state(self.conversation.start, update)

    # ---- main
    def manage_conversation(self, update, context, delete_first=False):
        """Master function for converastion"""
        state = None
        try:
            self.prev_state = self.prev_state or self.conversation.get_state(
                context.user_data.get("prev_state")
            )
            self.tData.update_telegram_data(update, context)
            telegram_id = self.tData.update.effective_chat.id
            # ---- check authorization
            if (
                self.conversation.users_list is not None
                and telegram_id not in self.conversation.users_list
            ):
                if (fbs := self.conversation.no_auth_state) :
                    return self.force_state(fbs, update)
                return self.NEXT
            # ---- start | first message
            if not self.tData.context.user_data:
                if delete_first:
                    update.message.delete()
                state = self.conversation.start
                self._init_context(state)
                self._send_message(state, self.tData.update.message.reply_text)
                return self.NEXT
            # ---- get data | next messages
            state = self.conversation.get_state(
                self.tData.context.user_data.get("state")
            )
            if self.tData.update.callback_query:
                data = self.tData.update.callback_query.data
                to_reply = self.tData.update.callback_query.edit_message_text
            else:
                if not state.regex and not state.handler:
                    self.tData.update.message.delete()
                    return self.NEXT
                data = (
                    state.handler
                    and state.handler(self.tData.prepare())
                    or (not state.handler and self.tData.update.message.text)
                )
                if state.regex and not match(state.regex, str(data)) or not data:
                    return self._wrong_message(state.regex, data)
                to_reply = self.tData.context.user_data.get("bot-msg").edit_text
                self.tData.update.message.delete()
            # ---- next stage
            typed_data = state.data_type(data) if data != "BACK" else "BACK"
            if not self._do_operations(state, typed_data) == self.EXIT_SIGNAL:
                state = self._change_state(typed_data)
                self._send_message(state, to_reply, save=False)
                if state == self.conversation.end:
                    self.tData.context.user_data.clear()
                    return ConversationHandler.END
            return self.NEXT
        except (Exception, BadRequest) as e:
            self._handle_bad_request(e, update, state)
