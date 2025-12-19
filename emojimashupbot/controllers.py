import asyncio
import emoji as emojilib
from .emojimashupers.main import mashuper
from .persistence.main import repository
from .models import Emoji, EmojiMashupRequest, EmojiMashupResult, EmojiMashupResultTelegram


async def mashup_emojis(bot_id, emojis: list[Emoji]) -> EmojiMashupResult:
    request = EmojiMashupRequest(emojis=emojis)

    # Find in repository cache
    mashup_id = request.mashup_id
    result = await repository().get_emoji_result_cache(mashup_id)
    if result and result.exists and result.result_telegram and result.result_telegram.bot_id == bot_id:
        return result

    # Find online
    result = await mashuper().mashup(emojis)
    #asyncio.create_task(repository().save_emoji_result_cache(result))
    return result


async def save_emoji_result(bot_id, result: EmojiMashupResult, telegram_sticker_file_id: str):
    if not result.result_telegram:
        result.result_telegram = EmojiMashupResultTelegram(
            bot_id=bot_id,
            sticker_file_id=telegram_sticker_file_id,
        )
        asyncio.create_task(repository().save_emoji_result_cache(result))


def parse_emojis(text: str) -> list[Emoji]:
    results = []
    for emoji_analysis in emojilib.analyze(text):
        results.append(Emoji(
            value=emoji_analysis.chars,
            unicodes=[Emoji.emoji_to_unicode(char) for char in emoji_analysis.chars],
            name=emoji_analysis.value.data["en"]
        ))
    return results
