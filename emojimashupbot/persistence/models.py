import datetime
from typing import ClassVar
from ..models import Emoji

import pydantic


class Metadata(pydantic.BaseModel):
    saved_on: datetime.datetime
    version: float


class EmojiCache(pydantic.BaseModel):
    METADATA_VERSION: ClassVar = 0.1

    id: str
    metadata: Metadata
    exist: bool
    emojis: list[Emoji] | None
    urls: list[str] | None = None
    telegram_sticker_file_id: str | None = None
