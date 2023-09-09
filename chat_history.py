import redis

import message as m
import chatgpt


class ChatHistory:
    def __init__(self, redis_server: redis.Redis):
        self.r = redis_server

    @staticmethod
    def user_num_tokens_key(user_id: int):
        return F"telegrambot:history:{user_id}:num_tokens"

    @staticmethod
    def user_history_key(user_id: int):
        return F"telegrambot:history:{user_id}:messages"

    def update_history(self, user_id: int, messages: list[m.Message]):
        user_num_tokens_key = self.user_num_tokens_key(user_id)
        user_history_key = self.user_history_key(user_id)

        num_user_tokens = self.r.get(user_num_tokens_key)
        if num_user_tokens is None:
            num_user_tokens = 0
        else:
            num_user_tokens = int(num_user_tokens)

        num_new_tokens = sum([m.num_tokens() for m in messages])

        if num_new_tokens > chatgpt.MAX_ALLOWED_TOKENS:
            # new messages are beyond limit, use exponential cut to reduce them
            self.clear_history(user_id)
            num_user_tokens = 0
            while messages and num_new_tokens > chatgpt.MAX_ALLOWED_TOKENS:
                first_message = messages[0]
                if len(first_message.message) <= 1:
                    # remove the top message if the messages are still too long
                    messages = messages[1:]
                    continue
                half_message_pos = len(first_message.message) // 2
                first_message.message = first_message.message[half_message_pos:]
                num_new_tokens = sum([m.num_tokens() for m in messages])
        else:
            while num_user_tokens + num_new_tokens > chatgpt.MAX_ALLOWED_TOKENS:
                message_str = self.r.lpop(user_history_key)
                message = m.str_to_message(message_str)
                num_user_tokens -= message.num_tokens()
                self.r.set(user_num_tokens_key, num_user_tokens)

        for message in messages:
            self.r.rpush(user_history_key, str(message))

        self.r.set(user_num_tokens_key, num_user_tokens + num_new_tokens)

    def get_history(self, user_id: int) -> list[m.Message]:
        return [
            m.str_to_message(m_str) for m_str in
            self.r.lrange(self.user_history_key(user_id), 0, -1)
        ]

    def clear_history(self, user_id: int):
        self.r.delete(self.user_history_key(user_id))
        self.r.set(self.user_num_tokens_key(user_id), 0)
