import abc
from ..models import Emoji, EmojiMashupResultComplete


class MashupInterface(abc.ABC):

    @abc.abstractmethod
    async def mashup(self, emojis: list[Emoji]) -> EmojiMashupResultComplete | None:
        pass
