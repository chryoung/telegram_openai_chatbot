import dataclasses
import os
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

    def num_tokens(self, model=None) -> int:
        """Return the number of tokens used."""
        if not model:
            model = os.getenv("OPENAI_TOKEN_COUNT_MODEL", "gpt-3.5-turbo-0613")
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
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            # Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.
            return self.num_tokens(model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            # Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
            return self.num_tokens(model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}."""
            )
        num_tokens = tokens_per_message
        num_tokens += len(encoding.encode(self.role))
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
