import aiogram
import aiogram.exceptions
from .models import TelegramBotInterface
from .dispatcher import setup_dispatcher
from ..settings import TelegramSettings
from ..utils import Singleton, get_id


class TelegramBot(TelegramBotInterface, Singleton):

    def __init__(self, settings: TelegramSettings):
        self.settings = settings
        self.dispatcher = setup_dispatcher(self)
        self.bot = aiogram.Bot(
            token=self.settings.bot_token.get_secret_value(),
        )
        self.bot_id = self.bot.id
        self.bot_username = ""

    async def init(self):
        self.bot_username = (await self.bot.get_me()).username

    async def run(self):
        await self.dispatcher.start_polling(self.bot)

    async def create_tmp_stickerset(self, stickers: list[aiogram.types.InputSticker]) -> str:
        stickerset_name = f"tmp_{get_id()}_by_{self.bot_username}"
        print("tmp stickerset name:", stickerset_name)
        await self.bot.create_new_sticker_set(
            user_id=self.settings.admins_chatids[0],
            name=stickerset_name,
            title=stickerset_name,
            stickers=stickers,
        )
        return stickerset_name

    async def delete_stickerset(self, stickerset_name: str) -> bool:
        try:
            return await self.bot.delete_sticker_set(stickerset_name)
        except aiogram.exceptions.TelegramBadRequest:
            return False
