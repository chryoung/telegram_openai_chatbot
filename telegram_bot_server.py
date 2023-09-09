import os
import asyncio
import time
import logging
import redis
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import openai
import functools
import chatgpt

from chat_history import ChatHistory
from message import UserMessage, AssistantMessage
from simple_lock import LockManager


ALLOWED_USERS = { int(user_id) for user_id in os.getenv('ALLOWED_USERS').split(',') }


r = redis.Redis(host=os.getenv('REDIS_SERVER', 'localhost'),
                port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
lockmgr = LockManager(r)
chat_history = ChatHistory(r)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
bot_logger = logging.getLogger("bot")
auth_logger = logging.getLogger("auth")

def auth():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            update = args[0]
            if update.message.from_user.id not in ALLOWED_USERS:
                auth_logger.warning(
                    F"Unauthroized user {update.message.from_user.id}")
                return
            return await func(*args)
        return wrapped
    return wrapper


def log_request():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            update = args[0]

            bot_logger.info(
                F"Request starts. Request = {func.__name__}, user id = {update.message.from_user.id}, chat id = {update.message.chat_id}, message id = {update.message.id}")

            result = await func(*args)

            bot_logger.info(
                F"Request ends. Request = {func.__name__}, user id = {update.message.from_user.id}, chat id = {update.message.chat_id}, message id = {update.message.id}")

            return result
        return wrapped
    return wrapper


@log_request()
@auth()
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lock = lockmgr.lock_gpt(user_id)
    if lock is not None:
        try:
            chat_history.clear_history(user_id)
            response = "Your chatting session has been restarted."
        finally:
            lockmgr.unlock(lock)
    else:
        response = "Chat service is busy..."

    if response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


@log_request()
@auth()
async def gptbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = UserMessage(update.message.text)

    lock = lockmgr.lock_gpt(user_id)
    if lock is None:
        response = 'Chat service is still thinking...'
    else:
        try:
            chat_history.update_history(user_id, [user_message])
            history = chat_history.get_history(user_id)
            response = chatgpt.get_response(update, history)
            chat_history.update_history(user_id, [AssistantMessage(response)])
        finally:
            lockmgr.unlock(lock)

    if response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


@log_request()
@auth()
async def gencode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Code generation is under construction.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_KEY')).build()

    restart_handler = CommandHandler('restart', restart)
    codegen_handler = CommandHandler('gencode', gencode)
    gptbot_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), gptbot)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(restart_handler)
    application.add_handler(codegen_handler)
    application.add_handler(gptbot_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
