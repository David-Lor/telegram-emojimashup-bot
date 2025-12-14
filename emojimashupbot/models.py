import hashlib
from typing import Annotated
import pydantic


EmojiChar = Annotated[str, pydantic.Field(max_length=1)]
EmojiUnicode = Annotated[str, pydantic.Field(max_length=6)]


class Emoji(pydantic.BaseModel):
    emoji: EmojiChar
    unicode: EmojiUnicode

    @classmethod
    def from_emoji(cls, emoji: EmojiChar) -> "Emoji":
        return cls(
            emoji=emoji,
            unicode=cls.emoji_to_unicode(emoji),
        )

    @staticmethod
    def emoji_to_unicode(emoji: EmojiChar) -> EmojiUnicode:
        return 'u{:X}'.format(ord(emoji)).lower()


class EmojiMashupRequest(pydantic.BaseModel):
    emojis: list[Emoji]

    @property
    def emojis_hash(self) -> str:
        hs = hashlib.new("sha256")
        for unicode in sorted(emoji.unicode for emoji in self.emojis):
            hs.update(unicode.encode())
        return hs.hexdigest()


class EmojiMashupResultBasic(EmojiMashupRequest):
    telegram_sticker_file_id: str | None = None


class EmojiMashupResultComplete(EmojiMashupResultBasic):
    result_url: str
    result_data: bytes
    result_extension: str = ".png"

    @property
    def emojis_map(self) -> dict[EmojiChar, EmojiUnicode]:
        return {emoji.emoji: emoji.unicode for emoji in self.emojis}

    @property
    def filename(self) -> str:
        s = "+".join(str(emoji.emoji) for emoji in self.emojis)
        return s + self.result_extension
