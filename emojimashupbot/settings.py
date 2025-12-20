import os
import yaml
import pydantic
from .utils import Singleton

SETTINGS_PATH = os.getenv("SETTINGS_PATH", "settings.yaml")


class MashupersSettings(pydantic.BaseModel):

    class Google(pydantic.BaseModel):
        revisions: list[int]

    google: Google


class PersistenceSettings(pydantic.BaseModel):

    class CouchDB(pydantic.BaseModel):
        url: str
        database: str = "emojimashup"
        username: str | None = None
        password: pydantic.SecretStr | None = None

    couchdb: CouchDB | None = None


class TelegramSettings(pydantic.BaseModel):
    bot_token: pydantic.SecretStr
    admins_chatids: list[int]
    sticker_size: list[int] = pydantic.Field(default=[512, 512], min_length=2, max_length=2)
    tmp_stickerset_basename: str = "tmp"


class MainSettings(pydantic.BaseModel, Singleton):
    telegram: TelegramSettings
    persistence: PersistenceSettings
    mashupers: MashupersSettings


def load_settings():
    with open(SETTINGS_PATH, "r") as f:
        settings = MainSettings.model_validate(yaml.safe_load(f))
    settings.set(settings)
    return settings
