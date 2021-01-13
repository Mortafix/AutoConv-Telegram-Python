class TelegramData:
    def __init__(self):
        self.update = None
        self.context = None
        self.telegram_id = None
        self.user_data = None
        self.states_data = None
        self.message = None
        self.exception = None

    def __str__(self):
        return (
            f"UPDATE {self.update}\n"
            f"CONTEXT {self.context}\n"
            f"TELEGRAM ID {self.telegram_id}\n"
            f"USER DATA {self.user_data}\n"
            f"STATES DATA {self.states_data}"
        )

    def update_telegram_data(self, update, context):
        self.update = update
        self.context = context

    def prepare(self):
        self.telegram_id = self.update.effective_chat.id
        self.udata = self.context.user_data
        self.sdata = self.udata.get("data") if self.udata else None
        self.message = self.update.message
        return self
