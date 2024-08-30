import os
import requests
import openai
import tiktoken
import logging

import message

openai.api_key = os.getenv("OPENAI_KEY")
openai.api_base = os.getenv("OPENAI_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")  # this may change in the future
deployment_name = os.getenv("OPENAI_DEPLOYMENT")

MAX_INPUT_TOKENS = int(os.getenv("OPENAI_MAX_INPUT_TOKENS", 1000))
MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", 500))

logger = logging.getLogger("chatgpt")


def get_response(update, history: list[message.Message]) -> str:
    """Get the completion response from the OpenAI service"""
    messages = history

    prompt = [m.to_dict() for m in messages]

    logger.info(
        F"Start to get chat completion for user id = {update.message.from_user.id}, chat id = {update.message.chat_id}, message id = {update.message.id}.")
    response = openai.ChatCompletion.create(
        engine=deployment_name, messages=prompt, max_tokens=MAX_OUTPUT_TOKENS)
    logger.info(
        F"Finished chat completion for user id = {update.message.from_user.id}, chat id = {update.message.chat_id}, message id = {update.message.id}.")

    return response['choices'][0]['message']['content']


MAX_ALLOWED_TOKENS = MAX_INPUT_TOKENS + MAX_OUTPUT_TOKENS
