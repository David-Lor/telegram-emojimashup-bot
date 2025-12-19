import aiogram
import emoji
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, ReactionTypeEmoji, InputSticker
from ..settings import MainSettings
from ..controllers import parse_emojis, mashup_emojis, save_emoji_result

dispatcher = aiogram.Dispatcher()


@dispatcher.message(Command("newset"))
async def handle_newset(message: aiogram.types.Message):
    # TODO STICKER_PNG_DIMENSIONS (debe ser 512x512 max)
    await message.bot.create_new_sticker_set(
        user_id=message.from_user.id,
        name=f"emojimashup_by_{MainSettings.get().telegram.bot_name}",
        title="Emoji Mashup",
        stickers=[InputSticker(
            sticker="CAACAgQAAxkDAAIHf2k6_9Eq9OPFQc-oPyMO0AeyhvlrAAIoGgACkG7ZUfXQNFxkgAliNgQ",
            format="static",
            emoji_list=["🐵", "🐌"]
        )]
    )


@dispatcher.message(Command("parse"))
async def handle_parse(message: aiogram.types.Message):
    import emoji
    await message.answer(f"len={len(message.text)}\n"
                         f"emoji.demojize={emoji.demojize(message.text)}\n"
                         f"parse_emojis={[e.emoji for e in parse_emojis(message.text)]}\n"
                         f"emoji.analyze={list(emoji.analyze(message.text))}\n")


@dispatcher.inline_query()
async def handle_inline_query(inline_query: aiogram.types.InlineQuery):
    print(f"Rx inline query: {inline_query.query}")
    if not (emojis := parse_emojis(inline_query.query)):
        return

    if result := await mashup_emojis(emojis):
        # TODO Esto manda la foto tal cual, debe ir como sticker
        # await inline_query.answer(
        #     results=[aiogram.types.InlineQueryResultPhoto(
        #         id=inline_query.query,
        #         photo_url=result.result_url,
        #         thumbnail_url=result.result_url,
        #     )],
        # )

        # TODO Esto no sirve:
        sticker = await inline_query.bot.upload_sticker_file(
            user_id=inline_query.from_user.id,
            sticker=BufferedInputFile(result.result_data, result.filename),
            sticker_format="static",
        )
        await inline_query.answer(
            results=[aiogram.types.InlineQueryResultCachedSticker(
                id=inline_query.query,
                type="sticker",
                sticker_file_id=sticker.file_id,
            )],
        )


@dispatcher.message()
async def handle_message(message: aiogram.types.Message):
    text = message.text
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
