import dataclasses
import tiktoken


class Message:
    def __init__(self, role: str, role_in_a_letter: str, message: str):
        self.role = role
        self.role_in_a_letter = role_in_a_letter
        self.message = message

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.message}

    def __str__(self) -> str:
        return F'{self.role_in_a_letter}:{self.message}'

    def num_tokens(self, model="gpt-3.5-turbo-0613") -> int:
        """Return the number of tokens used."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
        elif model == "gpt-3.5-turbo-0301":
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
        else:
            raise NotImplementedError(
                f"""num_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )

        num_tokens = tokens_per_message
        num_tokens += len(encoding.encode(self.message))

        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens


class SystemMessage(Message):
    def __init__(self, message: str = ''):
        super().__init__('system', 's', message)


class UserMessage(Message):
    def __init__(self, message: str = ''):
        super().__init__('user', 'u', message)


class AssistantMessage(Message):
    def __init__(self, message: str = ''):
        super().__init__('assistant', 'a', message)


class FunctionMessage(Message):
    def __init__(self, message: str = ''):
        super().__init__('function', 'f', message)


def str_to_message(s: str) -> Message:
    if len(s) < 3 or s[1] != ':':
        return None

    role = s[0]
    message = s[2:]

    if role == 's':
        return SystemMessage(message)
    elif role == 'u':
        return UserMessage(message)
    elif role == 'a':
        return AssistantMessage(message)
    elif role == 'f':
        return FunctionMessage(message)
    else:
        return None
