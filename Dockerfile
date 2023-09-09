FROM python:3.10.12-alpine
RUN pip install openai tiktoken python-telegram-bot redis
RUN mkdir /bot
COPY *.py /bot/
CMD python3 /bot/telegram_bot_server.py