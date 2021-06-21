from functools import reduce
from math import ceil
from re import match

from autoconv.telegram_data import TelegramData
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ConversationHandler


class AutoConvHandler:
    def __init__(self, conversation, telegram_state_name):
        self.conversation = conversation
        self.NEXT = telegram_state_name
        self.tData = TelegramData()
        self.prev_state = None
        self.curr_state = conversation.start
        self._bkup_state_routes, self._list_keyboard = None, None
        self.list_labels = None

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
                "doesn't exist as route of {state}."
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
            if state.list and isinstance(data, int):
                value = [
                    b
                    for b in reduce(lambda x, y: x + y, self._list_keyboard)
                    if b.callback_data is not None and b.callback_data == data
                ][0].text
            else:
                value = (
                    d
                    if (c := state.callback)
                    and (
                        d := c[0].get(
                            data
                            if not isinstance(data, int) and not str(data).isdigit()
                            else int(data)
                        )
                    )
                    else data
                )
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
            data_context.update({"error": False})
        elif data_context.get("error") is not None:
            data_context.pop("error")
        if self._bkup_state_routes:
            back_route = self._bkup_state_routes.pop("BACK", None)
            default_route = self._bkup_state_routes.pop(-1, None)
            self.conversation.add_routes(
                self.prev_state,
                self._bkup_state_routes,
                default=default_route,
                back=back_route,
            )
        self._bkup_state_routes = None
        return new_state

    def _wrong_message(self):
        """Handler for wrong message"""
        self.tData.update.message.delete()
        state = self.conversation.get_state(self.tData.context.user_data.get("state"))
        if (
            (self.tData.update.message.text and state.regex_error_text)
            or state.handler_error_text
        ) and not self.tData.context.user_data.get("error"):
            keyboard = self._build_keyboard(state)
            self.tData.context.user_data.update({"error": True})
            msg = (
                state.msg.replace("@@@", a)
                if state.action and (a := state.action(self.tData.prepare()))
                else state.msg
            )
            reply_msg = f"{msg}\n\n" + (
                (self.tData.update.message.text and state.regex_error_text)
                or state.handler_error_text
            )
            self.tData.context.user_data.get("bot-msg").edit_text(
                self.conversation.default_func(reply_msg),
                reply_markup=InlineKeyboardMarkup(keyboard),
                **state.kwargs,
            )
        return self.NEXT

    def _update_dynamic_list(self, state):
        """Update i and routes backup for dynamic list"""
        data = self.tData.context.user_data
        if (state_l := data.get("list")) :
            i = int(data.get("list_i"))
            if state.list_all:
                curr_list = self.list_labels or state_l
                elem_list = data.get("data").get(state.name)
                new_i = curr_list.index(elem_list) if elem_list in curr_list else i
            elif (
                not state.list_all
                and data.get("data").get(state.name) not in state.list_buttons
            ):
                new_i = i
            else:
                new_i = (i - 1, i + 1)[
                    data.get("data").get(state.name) == state.list_buttons[1]
                ]
            data.update({"list_i": new_i})
        else:
            state_l = state.list(self.tData.prepare())
            data.update({"list": state_l, "list_i": state.list_start})

    def _build_dynamic_list(self, state, keyboard):
        """Build dynamic list for current state"""
        self._bkup_state_routes = self.conversation.routes.get(state.name)
        data = self.tData.context.user_data
        state_l = data.get("list")
        basic_routes = {
            k + len(state_l): v
            for k, v in self.conversation.routes.get(state.name).items()
            if k not in ("BACK", -1)
        }
        for kl in keyboard:
            for button in kl:
                if (c := button.callback_data) is not None and isinstance(c, int):
                    button.callback_data += len(state_l)

        self.list_labels = state.list_labels and state.list_labels(self.tData.prepare())
        list_buttons = [
            [
                InlineKeyboardButton(
                    self.list_labels[r * state.list_max_row + i]
                    if self.list_labels
                    else b,
                    callback_data=r * state.list_max_row + i,
                )
                for i, b in enumerate(
                    state_l[
                        r * state.list_max_row : r * state.list_max_row
                        + state.list_max_row
                    ]
                    if state.list_all
                    else state.list_buttons
                )
            ]
            for r in range(
                ceil((len(state_l) if state.list_all else 1) / state.list_max_row)
            )
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
        ro, de, ba = state.routes(self.tData.prepare())
        self.conversation.add_routes(state, ro, de, ba)

    def _build_dynamic_keyboard(self, state):
        """Build dynamic keyboard for current state"""
        keyboard = state.build(self.tData.prepare())
        keyboard, size = keyboard if isinstance(keyboard, tuple) else (keyboard, None)
        state.add_keyboard(keyboard, size, max_row=state.max_row)

    def _build_dynamic_stuff(self, state):
        """Compute dynamic stuff: action > routes > keyboard > list"""
        data = self.tData.context.user_data
        if self.prev_state != self.curr_state and data.get("list"):
            data.pop("list")
            data.pop("list_i")
            self.list_labels = None
        if state.list:
            self._update_dynamic_list(state)
        if state.action:
            action_str = state.action(self.tData.prepare())
        if state.routes:
            self._build_dynamic_routes(state)
        if state.build:
            self._build_dynamic_keyboard(state)
        keyboard = self._build_keyboard(state)
        if state.list:
            keyboard = self._build_dynamic_list(state, keyboard)
        reply_msg = (
            state.msg.replace("@@@", action_str)
            if state.action and action_str
            else state.msg
        )
        return InlineKeyboardMarkup(keyboard), reply_msg

    def _init_context(self, state):
        """Initializate user data in context"""
        if not self.tData.context.user_data:
            self.tData.context.user_data.update(
                {"prev_state": None, "state": state.name, "error": False, "data": {}}
            )

    def _handle_bad_request(self, exception, update, msg, keyboard, state):
        """Handle every bad request"""
        self.tData.exception = exception
        if match("Message to edit not found", str(exception)):
            m = update.message.reply_text(msg, reply_markup=keyboard, **state.kwargs)
            self.tData.context.user_data.update({"bot-msg": m})
            return
        if not match("Message is not modified", str(exception)):
            if self.conversation.fallback_state:
                return self.force_state(self.conversation.fallback_state, update)
            raise exception

    def force_state(self, state, update):
        """Force a state in the conversation"""
        if isinstance(state, str):
            state = self.conversation.get_state(state)
        if state in self.conversation.state_list:
            # prepare data
            self._init_context(state)
            state = self._change_state(None, state=state)
            keyboard, reply_msg = self._build_dynamic_stuff(state)
            # check if the message exists
            old_msg = self.tData.context.user_data.get("bot-msg")
            send_msg = old_msg and old_msg.edit_text or update.message.reply_text
            try:
                m = send_msg(text=reply_msg, reply_markup=keyboard, **state.kwargs)
                self.tData.context.user_data.update({"bot-msg": m})
            except BadRequest as e:
                self._handle_bad_request(e, update, reply_msg, keyboard, state)
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

    def manage_conversation(self, update, context, delete_first=False):
        """Master function for converastion"""
        reply_msg, keyboard, state = None, None, None
        try:
            self.prev_state = self.prev_state or self.conversation.get_state(
                context.user_data.get("prev_state")
            )
            self.tData.update_telegram_data(update, context)
            telegram_id = self.tData.update.effective_chat.id
            # check authorization
            if (
                self.conversation.users_list is not None
                and telegram_id not in self.conversation.users_list
            ):
                if (fbs := self.conversation.no_auth_state) :
                    return self.force_state(fbs, update)
                return self.NEXT
            # start
            if not self.tData.context.user_data:
                if delete_first:
                    update.message.delete()
                state = self.conversation.start
                self._init_context(state)
                keyboard, reply_msg = self._build_dynamic_stuff(state)
                kwargs = self.conversation.defaults | state.kwargs
                msg = self.tData.update.message.reply_text(
                    self.conversation.default_func(reply_msg),
                    reply_markup=keyboard,
                    **kwargs,
                )
                self.tData.context.user_data.update({"bot-msg": msg})
                return self.NEXT
            # get data
            state = self.conversation.get_state(
                self.tData.context.user_data.get("state")
            )
            if self.tData.update.callback_query:
                data = self.tData.update.callback_query.data
                to_reply = self.tData.update.callback_query.edit_message_text
            else:
                data = (state.handler and state.handler(self.tData.prepare())) or (
                    state.regex and self.tData.update.message.text
                )
                if not state.regex and not state.handler:
                    self.tData.update.message.delete()
                    return self.NEXT
                if (
                    (
                        state.regex
                        and isinstance(data, str)
                        and not match(state.regex, data)
                    )
                    or (state.regex and not data)
                    or (state.handler and not data)
                ):
                    return self._wrong_message()
                to_reply = self.tData.context.user_data.get("bot-msg").edit_text
                self.tData.update.message.delete()
            # next stage
            typed_data = state.data_type(data) if data != "BACK" else "BACK"
            state = self._change_state(typed_data)
            keyboard, reply_msg = self._build_dynamic_stuff(state)
            kwargs = self.conversation.defaults | state.kwargs
            to_reply(
                self.conversation.default_func(reply_msg),
                reply_markup=keyboard,
                **kwargs,
            )
            if state == self.conversation.end:
                self.tData.context.user_data.clear()
                return ConversationHandler.END
            return self.NEXT
        except (Exception, BadRequest) as e:
            self._handle_bad_request(e, update, reply_msg, keyboard, state)
