import hashlib
import pydantic


class Emoji(pydantic.BaseModel):
    value: str
    unicodes: list[str]
    name: str


class EmojiMashupRequest(pydantic.BaseModel):
    emojis: list[Emoji]

    @property
    def mashup_id(self) -> str:
        hs = hashlib.new("sha256")
        for emoji in sorted(self.emojis, key=lambda _emoji: _emoji.name):
            hs.update(str(emoji.unicodes).encode())
        return hs.hexdigest()

    @property
    def emojis_icons_list(self):
        return [e.value for e in self.emojis]


class EmojiMashupResultURL(pydantic.BaseModel):
    url: str
    data: bytes | None = pydantic.Field(default=None, exclude=True)
    extension: str


class EmojiMashupResultTelegram(pydantic.BaseModel):
    bot_id: int
    sticker_file_id: str


class EmojiMashupResult(EmojiMashupRequest):
    exists: bool
    result_google: EmojiMashupResultURL | None = None
    result_telegram: EmojiMashupResultTelegram | None = None

    @property
    def filename(self) -> str | None:
        if self.result_google:
            s = "+".join(str(emoji.name) for emoji in self.emojis)
            return s + self.result_google.extension
        return None
