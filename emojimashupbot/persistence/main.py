from .persist_interface import PersistInterface
from .persist_couchdb import CouchDBPersist
from ..settings import MainSettings


async def init_repository():
    await CouchDBPersist(MainSettings.get().persistence.couchdb).set_this().init()


def repository() -> PersistInterface:
    return CouchDBPersist.get()
