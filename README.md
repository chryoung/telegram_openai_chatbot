# A Telegram Bot with Azure OpenAI

## Start

1. Apply a new bot on Telegram by talking to @BotFather.
1. Apply an [Azure] OpenAI account
1. Install docker and docker compose

Create a `env` file. Fill all the required fields. Make sure it's stored in a safe place!

```
OPENAI_ENDPOINT=<your_openai_endpoint>
OPENAI_KEY=<your_openai_key>
OPENAI_DEPLOYMENT=<your_openai_engine>
OPENAI_API_VERSION=<your_openai_version>
OPENAI_API_TYPE=<your_openai_type>
TELEGRAM_BOT_KEY=<you_telegram_bot_key>
REDIS_SERVER=redis
ALLOWED_USERS=<user_id_1>,<user_id_2>
```

Run `docker-compose up -d`
