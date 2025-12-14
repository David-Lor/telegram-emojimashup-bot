from .models import EmojiCache, Metadata
from ..models import EmojiMashupResultComplete, EmojiMashupResultBasic
from ..utils import get_now


def mashup_result_to_cache(result: EmojiMashupResultComplete) -> EmojiCache:
    return EmojiCache(
        id=result.emojis_hash,
        emojis=result.emojis_map,
        exist=True,
        urls=[result.result_url],
        telegram_sticker_file_id=result.telegram_sticker_file_id,
        metadata=Metadata(
            saved_on=get_now(),
            version=EmojiCache.METADATA_VERSION,
        ),
    )


def mashup_not_found_to_cache(mashup_id: str) -> EmojiCache:
    return EmojiCache(
        id=mashup_id,
        exist=False,
        emojis=None,
        metadata=Metadata(
            saved_on=get_now(),
            version=EmojiCache.METADATA_VERSION,
        ),
    )


def cache_to_mashup_result(cache: EmojiCache) -> EmojiMashupResultBasic:
    return EmojiMashupResultBasic(
        emojis=cache.emojis_map_to_array(),
        telegram_sticker_file_id=cache.telegram_sticker_file_id,
    )
