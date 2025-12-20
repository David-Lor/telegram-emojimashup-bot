import aiogram
from ..settings import TelegramSettings


class TelegramBotInterface:
    settings: TelegramSettings
    dispatcher: aiogram.Dispatcher
    bot: aiogram.Bot
    bot_id: int
    bot_username: str
    tmp_stickerset_name: str
