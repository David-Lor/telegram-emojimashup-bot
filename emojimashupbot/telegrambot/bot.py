import aiogram
import aiogram.exceptions
from .models import TelegramBotInterface
from .dispatcher import setup_dispatcher
from ..controllers import parse_emojis, mashup_emojis
from ..settings import TelegramSettings
from ..utils import Singleton


class TelegramBot(TelegramBotInterface, Singleton):

    def __init__(self, settings: TelegramSettings):
        self.settings = settings
        self.dispatcher = setup_dispatcher(self)
        self.bot = aiogram.Bot(
            token=self.settings.bot_token.get_secret_value(),
        )
        self.bot_id = self.bot.id
        self.bot_username = ""
        self.tmp_stickerset_name = ""

    async def init(self):
        self.bot_username = (await self.bot.get_me()).username
        # self.tmp_stickerset_name = self.settings.tmp_stickerset_basename + "_by_" + self.bot_username
        # await self._init_tmp_stickerset()

    async def run(self):
        await self.dispatcher.start_polling(self.bot)

    # TODO borrar tema de stickerset si finalmente no me sirve por el tema de recuperar el sticker que se quiere del set único común.

    async def _init_tmp_stickerset(self):
        try:
            await self.bot.get_sticker_set(self.tmp_stickerset_name)
        except aiogram.exceptions.TelegramBadRequest:
            await self._create_tmp_stickerset()

    async def _create_tmp_stickerset(self):
        tmp_emojis = parse_emojis("🗿🤓")
        tmp_emojis_result = await mashup_emojis(self.bot_id, tmp_emojis)

        await self.bot.create_new_sticker_set(
            user_id=self.settings.admins_chatids[0],
            name=self.tmp_stickerset_name,
            title=self.tmp_stickerset_name,
            stickers=[aiogram.types.InputSticker(
                sticker=aiogram.types.BufferedInputFile(
                    file=tmp_emojis_result.result_google.data,
                    filename=tmp_emojis_result.filename,
                ),
                format="static",
                emoji_list=tmp_emojis_result.emojis_icons_list,
            )]
        )
