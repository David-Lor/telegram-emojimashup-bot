from .models import EmojiCache, Metadata
from ..models import EmojiMashupResultComplete, EmojiMashupResultBasic
from ..utils import get_now


def format_cache_id(mashup_id, metadata_version=EmojiCache.METADATA_VERSION) -> str:
    return f"{metadata_version}:{mashup_id}"


def mashup_result_to_cache(result: EmojiMashupResultComplete | None, mashup_id: str | None = None) -> EmojiCache:
    metadata = Metadata(
        saved_on=get_now(),
        version=EmojiCache.METADATA_VERSION,
    )
    cache_id = format_cache_id(
        metadata_version=metadata.version,
        mashup_id=mashup_id or result.emojis_hash,
    )

    return EmojiCache(
        id=cache_id,
        exist=bool(result),
        emojis=result.emojis if result else None,
        urls=[result.result_url] if result else None,
        telegram_sticker_file_id=result.telegram_sticker_file_id if result else None,
        metadata=metadata,
    )


def cache_to_mashup_result(cache: EmojiCache) -> EmojiMashupResultBasic:
    return EmojiMashupResultBasic(
        emojis=[],
        telegram_sticker_file_id=cache.telegram_sticker_file_id,
    )
