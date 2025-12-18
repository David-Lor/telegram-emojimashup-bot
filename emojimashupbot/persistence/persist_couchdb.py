import aiocouch
from .persist_interface import PersistInterface
from .models import EmojiCache
from .mappers import mashup_result_to_cache, cache_to_mashup_result, format_cache_id
from ..models import EmojiMashupResultComplete, EmojiMashupResultBasic
from ..settings import PersistenceSettings
from ..utils import Singleton


class CouchDBPersist(PersistInterface, Singleton):

    def __init__(self, settings: PersistenceSettings.CouchDB):
        self.settings = settings
        self.connection: aiocouch.CouchDB | None = None
        self.db: aiocouch.Database | None = None

    async def init(self):
        self.connection = aiocouch.CouchDB(
            self.settings.url,
            user=self.settings.username,
            password=self.settings.password.get_secret_value() if self.settings.password else None,
        )
        await self.connection.check_credentials()
        # noinspection PyUnresolvedReferences
        self.db = await self.connection[self.settings.database]
        print("CouchDB connected")

    async def close(self):
        if self.connection:
            await self.connection.close()
            print("CouchDB closed")
            self.db = None
            self.connection = None

    async def save_emoji_result_cache(self, result: EmojiMashupResultComplete):
        result_save = mashup_result_to_cache(result)
        await self._save_emoji_result_cache(result_save)

    async def save_emoji_result_cache_not_found(self, mashup_id: str):
        result_save = mashup_result_to_cache(result=None, mashup_id=mashup_id)
        await self._save_emoji_result_cache(result_save)

    async def _save_emoji_result_cache(self, result_save: EmojiCache):
        data = result_save.model_dump(mode="json", exclude={"id"}, exclude_none=True)
        print("Save:", data)
        doc = await self.db.create(
            id=result_save.id,
            data=data,
        )
        await doc.save()

    async def get_emoji_result_cache(self, mashup_id: str) -> EmojiMashupResultBasic | None:
        try:
            doc = await self.db.get(format_cache_id(mashup_id))
            parsed_doc = EmojiCache(id=doc.id, **doc.data)
            return cache_to_mashup_result(parsed_doc)
        except aiocouch.exception.NotFoundError:
            return None
