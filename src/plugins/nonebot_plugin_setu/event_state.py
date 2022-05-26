from sre_parse import State
import time

class EventState:

    user_id: str = ""
    state: bool = False
    ts: int = -1

    @classmethod
    def block(cls, user_id: str):

        cls.state = True
        cls.user_id = user_id
        cls.ts = int(time.time())

    @classmethod
    def open(cls):

        cls.state = False

    @classmethod
    def is_block(cls):

        if int(time.time()) - cls.ts > 60:
            return False
        else:
            return cls.state