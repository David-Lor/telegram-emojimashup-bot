import datetime
from typing import ClassVar
from ..utils import get_now

import pydantic


class Metadata(pydantic.BaseModel):
    METADATA_VERSION: ClassVar = 0.2

    version: float
    saved_on: datetime.datetime

    @classmethod
    def new(cls):
        return cls(
            version=cls.METADATA_VERSION,
            saved_on=get_now(),
        )
