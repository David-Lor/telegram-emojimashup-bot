import abc
from ..models import EmojiMashupResultComplete, EmojiMashupResultBasic


class PersistInterface(abc.ABC):

    async def init(self):
        pass

    async def close(self):
        pass

    @abc.abstractmethod
    async def save_emoji_result_cache(self, result: EmojiMashupResultComplete):
        pass

    @abc.abstractmethod
    async def save_emoji_result_cache_not_found(self, mashup_id: str):
        pass

    @abc.abstractmethod
    async def get_emoji_result_cache(self, mashup_id: str) -> EmojiMashupResultBasic | None:
        pass
