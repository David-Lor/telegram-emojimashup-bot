import uuid
import asyncio
import aiogram
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, ReactionTypeEmoji, InputSticker
from .models import TelegramBotInterface
from ..controllers import parse_emojis, mashup_emojis, save_emoji_result


def setup_dispatcher(bot: TelegramBotInterface) -> aiogram.Dispatcher:
    dispatcher = aiogram.Dispatcher()


    @dispatcher.message(Command("newset"))
    async def handle_newset(message: aiogram.types.Message):  # TODO Remove
        print("Rx newset")
        stickerset_name = f"emojimashup_by_{bot.bot_username}"
        try:
            await bot.bot.delete_sticker_set(stickerset_name)
        except Exception as e:
            pass

        r = await message.bot.create_new_sticker_set(
            user_id=message.from_user.id,
            name=stickerset_name,
            title=f"Emoji Mashup {stickerset_name}",
            stickers=[InputSticker(
                sticker="CAACAgQAAxkDAAIIC2lGz4zp5AfRPcwaKSjFFTqxKTGHAALAGQACKH85UvaaFOqNuuE9NgQ",
                format="static",
                emoji_list=["🥸","🗿"]
            )]
        )
        print("create new sticker set:", r)

        await message.answer(f"New set created: https://t.me/addstickers/{stickerset_name}")


    @dispatcher.inline_query()
    async def handle_inline_query(inline_query: aiogram.types.InlineQuery):
        print(f"Rx inline query: {inline_query.query}")
        if not (emojis := parse_emojis(inline_query.query)):
            return

        result = await mashup_emojis(bot.bot_id, emojis)
        # TODO Tratar emojis cacheados
        if result.result_google and result.result_google.data:
            sticker_tmp = await inline_query.bot.upload_sticker_file(
                user_id=inline_query.from_user.id,
                sticker=BufferedInputFile(result.result_google.data, result.filename),
                sticker_format="static",
            )

            # await bot.bot.add_sticker_to_set(
            #     user_id=bot.settings.admins_chatids[0],
            #     name=bot.tmp_stickerset_name,
            #     sticker=aiogram.types.InputSticker(
            #         sticker=sticker_tmp.file_id,
            #         format="static",
            #         emoji_list=result.emojis_icons_list,
            #     )
            # )
            #
            # await asyncio.sleep(1)
            # tmp_stickerset = await bot.bot.get_sticker_set(bot.tmp_stickerset_name)
            # sticker_in_tmp_stickerset = next(
            #     sticker for sticker in tmp_stickerset.stickers
            #     if sticker.file_unique_id == sticker_tmp.file_unique_id
            # )
            # # await bot.bot.delete_sticker_from_set(sticker_in_tmp_stickerset.file_id)
            # await inline_query.answer(
            #     results=[aiogram.types.InlineQueryResultCachedSticker(
            #         id="foo",
            #         type="sticker",
            #         sticker_file_id=sticker_in_tmp_stickerset.file_id,
            #     )],
            # )

            # TODO Intento 2 creando un stickerset por petición, costoso pero efectivo

            tmp_stickerset_name = f"tmp_{uuid.uuid4().hex}_by_{bot.bot_username}"
            print("tmp stickerset name:", tmp_stickerset_name)
            try:
                await bot.bot.create_new_sticker_set(
                    user_id=inline_query.from_user.id,
                    name=tmp_stickerset_name,
                    title=tmp_stickerset_name,
                    stickers=[InputSticker(
                        sticker=sticker_tmp.file_id,
                        format="static",
                        emoji_list=result.emojis_icons_list,
                    )]
                )

                tmp_stickerset = await bot.bot.get_sticker_set(tmp_stickerset_name)
                sticker_in_tmp_stickerset = tmp_stickerset.stickers[0]
                asyncio.create_task(save_emoji_result(bot.bot_id, result, sticker_in_tmp_stickerset.file_id))
                await inline_query.answer(
                    results=[aiogram.types.InlineQueryResultCachedSticker(
                        id="foo",
                        type="sticker",
                        sticker_file_id=sticker_in_tmp_stickerset.file_id,
                    )],
                )

            finally:
                # pass
                async def __delete_sticker_set():
                    try:
                        await bot.bot.delete_sticker_set(tmp_stickerset_name)
                    except Exception as ex:
                        print("Error deleting tmp stickerset:", ex)
                asyncio.create_task(__delete_sticker_set())


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
