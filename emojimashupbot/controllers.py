import io
import asyncio
import aiogram
import emoji as emojilib
from PIL import Image
from .settings import MainSettings
from .emojimashupers.main import mashuper
from .telegrambot.models import TelegramBotInterface
from .persistence.main import repository
from .models import Emoji, EmojiMashupRequest, EmojiMashupResult, EmojiMashupResultTelegram


async def mashup_emojis(bot: TelegramBotInterface, emojis: list[Emoji]) -> EmojiMashupResult:
    request = EmojiMashupRequest(emojis=emojis)

    # Find in repository cache
    mashup_id = request.mashup_id
    result = await repository().get_emoji_result_cache(mashup_id)

    # Cached in Telegram
    if result and result.exists and result.result_telegram and result.result_telegram.bot_id == bot.bot_id:
        return result

    # Cached URL, not sent to Telegram
    # TODO Download from URL

    # Find & Download Online
    result = await mashuper().mashup(emojis)
    if not result.exists:
        # Save when not exists. When does exist, will be saved after sending as sticker.
        asyncio.create_task(repository().save_emoji_result_cache(result))
        return result

    # Resize to appropiate Telegram sticker dimensions
    result.result_google.data = resize_sticker(
        data=result.result_google.data,
        extension=result.result_google.extension,
    )

    # Cache in Telegram servers
    sticker_file_id = await cache_sticker_in_telegram(bot, result)
    await save_emoji_result(bot.bot_id, result, sticker_file_id)

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


async def cache_sticker_in_telegram(bot: TelegramBotInterface, result: EmojiMashupResult) -> str:
    sticker_file = await bot.bot.upload_sticker_file(
        user_id=bot.settings.admins_chatids[0],
        sticker=aiogram.types.BufferedInputFile(result.result_google.data, result.filename),
        sticker_format="static",
    )
    input_sticker = aiogram.types.InputSticker(
        sticker=sticker_file.file_id,
        format="static",
        emoji_list=result.emojis_icons_list,
    )
    tmp_stickerset_name = await bot.create_tmp_stickerset([input_sticker])

    try:
        tmp_stickerset = await bot.bot.get_sticker_set(tmp_stickerset_name)
        sticker_in_tmp_stickerset = tmp_stickerset.stickers[0]
        asyncio.create_task(save_emoji_result(bot.bot_id, result, sticker_in_tmp_stickerset.file_id))
        print("Sticker cached in Telegram", tmp_stickerset_name, sticker_in_tmp_stickerset.file_id)
        return sticker_in_tmp_stickerset.file_id

    finally:
        asyncio.create_task(bot.delete_stickerset(tmp_stickerset_name))
