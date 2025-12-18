import asyncio
import emoji as emojilib
from .emojimashupers.main import mashuper
from .persistence.main import repository
from .models import Emoji, EmojiMashupRequest, EmojiMashupResultComplete, EmojiMashupResultBasic


async def mashup_emojis(emojis: list[Emoji]) -> EmojiMashupResultBasic | EmojiMashupResultComplete | None:
    request = EmojiMashupRequest(
        emojis=emojis,
    )

    # Find in repository cache
    mashup_id = request.emojis_hash
    if result := await repository().get_emoji_result_cache(mashup_id):
        # TODO replantear modelos de domain y persistencia. Necesito obtener el "exists" desde aquí
        return result

    # Find online
    if result := await mashuper().mashup(emojis):
        return result

    # Not found
    asyncio.create_task(
        repository().save_emoji_result_cache_not_found(mashup_id)
    )
    return None


async def save_emoji_result(result: EmojiMashupResultComplete, telegram_sticker_file_id: str):
    if not result.telegram_sticker_file_id:
        result.telegram_sticker_file_id = telegram_sticker_file_id
        asyncio.create_task(
            repository().save_emoji_result_cache(result)
        )


def parse_emojis(text: str) -> list[Emoji]:
    results = []
    for emoji_analysis in emojilib.analyze(text):
        results.append(Emoji(
            value=emoji_analysis.chars,
            unicodes=[Emoji.emoji_to_unicode(char) for char in emoji_analysis.chars],
            name=emoji_analysis.value.data["en"]
        ))
    return results
