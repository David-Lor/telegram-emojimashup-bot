import hashlib
import pydantic


class Emoji(pydantic.BaseModel):
    value: str
    unicodes: list[str]
    name: str

    @staticmethod
    def emoji_to_unicode(emoji: str) -> str:
        return 'u{:X}'.format(ord(emoji)).lower()


class EmojiMashupRequest(pydantic.BaseModel):
    emojis: list[Emoji]

    @property
    def emojis_hash(self) -> str:
        hs = hashlib.new("sha256")
        for emoji in sorted(self.emojis, key=lambda emoji: emoji.name):
            hs.update(str(emoji.unicodes).encode())
        return hs.hexdigest()


class EmojiMashupResultBasic(EmojiMashupRequest):
    telegram_sticker_file_id: str | None = None


class EmojiMashupResultComplete(EmojiMashupResultBasic):
    result_url: str
    result_data: bytes
    result_extension: str = ".png"

    @property
    def filename(self) -> str:
        s = "+".join(str(emoji.name) for emoji in self.emojis)
        return s + self.result_extension
