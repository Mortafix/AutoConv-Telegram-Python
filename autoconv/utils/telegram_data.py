class TelegramData:
    def __init__(self, autoconv, users):
        self.autoconv = autoconv
        self.update = None
        self.context = None
        self.telegram_id = None
        self.udata = None
        self.sdata = None
        self.message = None
        self.chat_type = None
        self.exception = None
        self.users = users

    def __str__(self):
        return (
            f"UPDATE {self.update}\n"
            f"CONTEXT {self.context}\n"
            f"TELEGRAM ID {self.telegram_id}\n"
            f"USER DATA {self.udata}\n"
            f"STATES DATA {self.sdata}\n"
            f"AUTH USERS {self.users}"
        )

    # ---- Update functions

    def update_telegram_data(self, update, context):
        """Simple info update in TelegramData"""
        self.update = update
        self.context = context

    def prepare(self):
        """Preparing all the update info for dynamic stuff in handler"""
        self.message = self.update.message or self.update.callback_query.message
        self.telegram_id = self.update.effective_user.id
        self.chat_type = self.message.chat.type
        self.udata = self.context.user_data
        self.sdata = self.udata.get("data") if self.udata else None
        self.message = self.update.message
        return self

    # ---- Public function

    def save(self, *args, **kwargs):
        """Save key:value in user_data space"""
        self.context.user_data.update(*args, **kwargs)
        self.prepare()

    def add(self, key, value):
        """Add some value to a already stored key in user_data"""
        prev_value = self.udata.get(key)
        self.context.user_data.update({key: prev_value + value})
        self.prepare()
        return prev_value + value

    def get_or_set(self, key, set_value):
        """Get or set a value associated to a key in user_data"""
        if key not in self.udata:
            self.save({key: set_value})
        return self.udata.get(key)

    def delete(self, key, pop_value=None):
        """Delete a key in user_data"""
        value = self.context.user_data.pop(key, pop_value)
        self.prepare()
        return value
