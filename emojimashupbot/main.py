import asyncio
from .settings import load_settings
from .emojimashupers.main import init_mashupers
from .persistence.main import init_repository, repository
from .telegrambot.main import init_bot, bot


async def amain():
    load_settings()
    init_mashupers()

    # Init
    await asyncio.gather(
        init_repository(),
        init_bot(),
    )

    await bot().run()

    # Teardown
    await repository().close()


def main():
    asyncio.run(amain())
