import aiogram
from .dispatcher import dispatcher
from ..settings import TelegramSettings
from ..utils import Singleton


class TelegramBot(Singleton):

    def __init__(self, settings: TelegramSettings):
        self.settings = settings
        self.dispatcher = dispatcher
        self.bot = aiogram.Bot(
            token=self.settings.bot_token.get_secret_value(),
        )

    async def init(self):
        pass

    async def run(self):
        await self.dispatcher.start_polling(self.bot)
