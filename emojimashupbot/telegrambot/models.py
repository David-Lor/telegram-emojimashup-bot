import abc
import aiogram
from ..settings import TelegramSettings


class TelegramBotInterface(abc.ABC):
    settings: TelegramSettings
    dispatcher: aiogram.Dispatcher
    bot: aiogram.Bot
    bot_id: int
    bot_username: str
    tmp_stickerset_name: str

    @abc.abstractmethod
    async def create_tmp_stickerset(self, stickers: list[aiogram.types.InputSticker]) -> str: ...

    @abc.abstractmethod
    async def delete_stickerset(self, stickerset_name: str) -> bool: ...
