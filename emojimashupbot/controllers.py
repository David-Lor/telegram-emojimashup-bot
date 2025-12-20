import io
import asyncio
import emoji as emojilib
from PIL import Image
from .settings import MainSettings
from .emojimashupers.main import mashuper
from .persistence.main import repository
from .models import Emoji, EmojiMashupRequest, EmojiMashupResult, EmojiMashupResultTelegram


async def mashup_emojis(bot_id: int, emojis: list[Emoji]) -> EmojiMashupResult:
    request = EmojiMashupRequest(emojis=emojis)

    # Find in repository cache
    mashup_id = request.mashup_id
    result = await repository().get_emoji_result_cache(mashup_id)
    if result and result.exists and result.result_telegram and result.result_telegram.bot_id == bot_id:
        return result

    # TODO Posibilidad de cacheado pero no enviado x telegram

    # TODO Enviar el sticker a telegram con el truquillo del stickerset temporal, para tenerlo siempre cacheado? y no tener esta lógica compleja en TG

    # Find online
    result = await mashuper().mashup(emojis)
    if result.exists:
        result.result_google.data = resize_sticker(
            data=result.result_google.data,
            extension=result.result_google.extension,
        )
    else:
        # Save when not exists. When does exist, will be saved after sending as sticker.
        asyncio.create_task(repository().save_emoji_result_cache(result))

    return result


async def save_emoji_result(bot_id: int, result: EmojiMashupResult, telegram_sticker_file_id: str):
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
            unicodes=[emoji_to_unicode(char) for char in emoji_analysis.chars],
            name=emoji_analysis.value.data["en"]
        ))
    return results


def emoji_to_unicode(emoji_char: str) -> str:
    return 'u{:X}'.format(ord(emoji_char)).lower()


def resize_sticker(data: bytes, extension: str) -> bytes:
    size = MainSettings.get().telegram.sticker_size
    output = io.BytesIO()
    with Image.open(io.BytesIO(data)) as img:
        with img.resize(size) as img_resized:
            img_resized.save(output, format=extension.upper())

    return output.getvalue()
