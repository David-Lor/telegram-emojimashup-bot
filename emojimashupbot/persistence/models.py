import datetime
from typing import ClassVar
from ..models import Emoji, EmojiChar, EmojiUnicode

import pydantic


class Metadata(pydantic.BaseModel):
    saved_on: datetime.datetime
    version: float


class EmojiCache(pydantic.BaseModel):
    METADATA_VERSION: ClassVar = 1.0

    id: str
    metadata: Metadata
    exist: bool
    emojis: dict[EmojiChar, EmojiUnicode] | None
    urls: list[str] | None = None
    telegram_sticker_file_id: str | None = None

    def emojis_map_to_array(self) -> list[Emoji]:
        return [
            Emoji(emoji=emoji, unicode=unicode)
            for emoji, unicode in self.emojis.items()
        ]
