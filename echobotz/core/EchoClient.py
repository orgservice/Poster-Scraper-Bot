from pyrogram import Client
from pyrogram.enums import ParseMode
from asyncio import Lock
from inspect import signature
from logging import getLogger

from config import Config

LOGGER = getLogger(__name__)


class EchoBot:
    _lock = Lock()

    bot: Client | None = None
    ID = 0
    USERNAME = ""

    @classmethod
    def echoClient(cls, *args, **kwargs):
        kwargs["api_id"] = Config.API_ID
        kwargs["api_hash"] = Config.API_HASH
        kwargs["parse_mode"] = ParseMode.HTML
        kwargs["in_memory"] = True

        for param, value in {
            "skip_updates": False,
        }.items():
            if param in signature(Client.__init__).parameters:
                kwargs[param] = value

        return Client(*args, **kwargs)

    @classmethod
    async def start(cls):
        async with cls._lock:
            LOGGER.info("Creating EchoBot client")

            cls.bot = cls.echoClient(
                "EchoBotz",
                bot_token=Config.BOT_TOKEN,
                workers=100,
            )

            await cls.bot.start()

            me = cls.bot.me
            cls.ID = me.id
            cls.USERNAME = me.username

            LOGGER.info(f"EchoBot @{cls.USERNAME} Started")

    @classmethod
    async def stop(cls):
        async with cls._lock:
            if cls.bot:
                await cls.bot.stop()
                cls.bot = None
                LOGGER.info("EchoBot stopped")
