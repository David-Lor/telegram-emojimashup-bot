import abc
from ..models import Emoji, EmojiMashupResult


class MashupInterface(abc.ABC):

    @abc.abstractmethod
    async def mashup(self, emojis: list[Emoji]) -> EmojiMashupResult:
        pass
