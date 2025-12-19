import abc
from ..models import EmojiMashupResult


class PersistInterface(abc.ABC):

    async def init(self):
        pass

    async def close(self):
        pass

    @abc.abstractmethod
    async def save_emoji_result_cache(self, result: EmojiMashupResult):
        pass

    @abc.abstractmethod
    async def get_emoji_result_cache(self, mashup_id: str) -> EmojiMashupResult | None:
        pass
