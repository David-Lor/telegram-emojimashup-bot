import aiocouch
from .persist_interface import PersistInterface
from .models import Metadata
from ..models import EmojiMashupResult
from ..settings import PersistenceSettings
from ..utils import Singleton, get_now


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

    async def save_emoji_result_cache(self, result: EmojiMashupResult):
        doc_id, doc = self.Mappers.result_to_doc(result)
        print("Save:", doc_id, doc)
        try:
            create = await self.db.create(
                id=doc_id,
                data=doc,
            )
            await create.save()
        except aiocouch.exception.ConflictError:
            print("Update instead:", doc_id, doc)
            saved = await self.db.get(doc_id)
            saved.update(doc)
            await saved.save()

    async def get_emoji_result_cache(self, mashup_id: str) -> EmojiMashupResult | None:
        try:
            doc = await self.db.get(self.Mappers.format_doc_id(Metadata.METADATA_VERSION, mashup_id))
            result = self.Mappers.doc_to_result(doc.data)
            print("Read:", result)
            return result
        except aiocouch.exception.NotFoundError:
            return None


    class Mappers:

        @classmethod
        def result_to_doc(cls, result: EmojiMashupResult) -> tuple[str, dict]:
            metadata = Metadata.new()
            doc_id = cls.format_doc_id(metadata.version, result.mashup_id)
            doc = dict(
                **result.model_dump(mode="json", exclude={"id"}, exclude_none=True),
                metadata=metadata.model_dump(mode="json"),
            )
            return doc_id, doc

        @classmethod
        def doc_to_result(cls, doc: dict) -> EmojiMashupResult:
            return EmojiMashupResult(**doc)

        @classmethod
        def format_doc_id(cls, metadata_version, mashup_id) -> str:
            return f"{metadata_version}:{mashup_id}"
