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

        result = await mashup_emojis(bot.bot_id, emojis)
        # TODO Tratar emojis cacheados
        if result.result_google and result.result_google.data:
            sticker_file = await inline_query.bot.upload_sticker_file(
                user_id=inline_query.from_user.id,
                sticker=BufferedInputFile(result.result_google.data, result.filename),
                sticker_format="static",
            )
            input_sticker = InputSticker(
                sticker=sticker_file.file_id,
                format="static",
                emoji_list=result.emojis_icons_list,
            )

            tmp_stickerset_name = await bot.create_tmp_stickerset([input_sticker])

            try:
                tmp_stickerset = await bot.bot.get_sticker_set(tmp_stickerset_name)
                sticker_in_tmp_stickerset = tmp_stickerset.stickers[0]
                await asyncio.gather(
                    save_emoji_result(bot.bot_id, result, sticker_in_tmp_stickerset.file_id),
                    bot.bot.answer_inline_query(
                        inline_query_id=inline_query.id,
                        results=[aiogram.types.InlineQueryResultCachedSticker(
                            id="foo",
                            type="sticker",
                            sticker_file_id=sticker_in_tmp_stickerset.file_id,
                        )],
                    )
                )

            finally:
                asyncio.create_task(bot.delete_stickerset(tmp_stickerset_name))


    @dispatcher.message()
    async def handle_message(message: aiogram.types.Message):
        if not (text := message.text):
            return

        print(f"Rx message: {text}")

        if not (emojis := parse_emojis(text)):
            return

        result = await mashup_emojis(bot_id=message.bot.id, emojis=emojis)
        if result.result_telegram:
            sticker_file = result.result_telegram.sticker_file_id
        elif result.result_google and result.result_google.data:
            sticker_file = BufferedInputFile(
                file=result.result_google.data,
                filename=result.filename,
            )
        else:
            await message.react([ReactionTypeEmoji(emoji="👎")])
            return

        sticker = await message.answer_sticker(
            reply_to_message_id=message.message_id,
            sticker=sticker_file,
        )

        print("Sticker id:", sticker.sticker.file_id)
        await save_emoji_result(
            bot_id=message.bot.id,
            result=result,
            telegram_sticker_file_id=sticker.sticker.file_id,
        )

    return dispatcher
