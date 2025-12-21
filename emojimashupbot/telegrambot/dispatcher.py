import uuid
import asyncio
import aiogram
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, ReactionTypeEmoji, InputSticker
from .models import TelegramBotInterface
from ..controllers import parse_emojis, mashup_emojis, save_emoji_result


def setup_dispatcher(bot: TelegramBotInterface) -> aiogram.Dispatcher:
    dispatcher = aiogram.Dispatcher()


    @dispatcher.inline_query()
    async def handle_inline_query(inline_query: aiogram.types.InlineQuery):
        if not inline_query.query:
            return

        print(f"Rx inline query: {inline_query.query}")
        if not (emojis := parse_emojis(inline_query.query)):
            return

        result = await mashup_emojis(bot, emojis)
        if result.exists and result.result_telegram:
            await bot.bot.answer_inline_query(
                inline_query_id=inline_query.id,
                results=[aiogram.types.InlineQueryResultCachedSticker(
                    id="foo",
                    type="sticker",
                    sticker_file_id=result.result_telegram.sticker_file_id,
                )],
            )


    @dispatcher.message()
    async def handle_message(message: aiogram.types.Message):
        if not (text := message.text):
            return

        print(f"Rx message: {text}")

        if not (emojis := parse_emojis(text)):
            return

        result = await mashup_emojis(bot, emojis)
        if not result.exists or not result.result_telegram:
            await message.react([ReactionTypeEmoji(emoji="👎")])
            return

        await message.answer_sticker(
            reply_to_message_id=message.message_id,
            sticker=result.result_telegram.sticker_file_id,
        )

    return dispatcher
