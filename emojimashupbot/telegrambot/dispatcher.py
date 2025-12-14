import aiogram
import emoji
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, ReactionTypeEmoji, InputSticker
from ..settings import MainSettings
from ..controllers import mashup_emojis, save_emoji_result

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


@dispatcher.message()
async def handle_message(message: aiogram.types.Message):
    text = message.text
    print(f"Rx message: {text}")

    emojis = [char for char in text if emoji.is_emoji(char)]
    print(f"Identified emojis: {emojis}")

    if result := await mashup_emojis(emojis):
        if result.telegram_sticker_file_id:
            sticker_file = result.telegram_sticker_file_id
        else:
            sticker_file = BufferedInputFile(result.result_data, result.filename)

        sticker = await message.answer_sticker(
            reply_to_message_id=message.message_id,
            sticker=sticker_file,
        )

        print("Sticker id:", sticker.sticker.file_id)
        await save_emoji_result(result, sticker.sticker.file_id)

    else:
        await message.react([ReactionTypeEmoji(emoji="👎")])
