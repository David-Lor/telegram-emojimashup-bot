from .bot import TelegramBot
from ..settings import MainSettings


async def init_bot():
    await TelegramBot(MainSettings.get().telegram).set_this().init()


def bot() -> TelegramBot:
    return TelegramBot.get()
