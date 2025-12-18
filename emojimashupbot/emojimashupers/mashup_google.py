import random
import httpx
from .mashup_interface import MashupInterface
from ..models import Emoji, EmojiMashupResultComplete
from ..settings import MashupersSettings
from ..utils import Singleton, AsyncPool


class GoogleMashup(MashupInterface, Singleton):

    def __init__(self, settings: MashupersSettings.Google):
        self.settings = settings

    async def mashup(self, emojis: list[Emoji]) -> EmojiMashupResultComplete | None:
        if len(emojis) != 2:
            raise ValueError("Google mashup supports only 2 emojis")

        emoji1, emoji2 = emojis
        emojis_combinations = [(emoji1, emoji2), (emoji2, emoji1)]
        
        urls = list()
        for emoji1, emoji2 in emojis_combinations:
            for revision in self.settings.revisions:
                unicode1 = "-".join(emoji1.unicodes)
                unicode2 = "-".join(emoji2.unicodes)
                url = f"https://www.gstatic.com/android/keyboard/emojikitchen/{revision}/{unicode1}/{unicode1}_{unicode2}.png"
                urls.append(url)

        random.shuffle(urls)
        runner = AsyncPool[httpx.Response](concurrency_limit=5)

        async with httpx.AsyncClient() as client:
            for url in urls:
                runner.add_task(self._request_mashup(client, url, runner))
            await runner.run()

        if responses := [r for r in runner.results if r]:
            response = responses[0]
            return EmojiMashupResultComplete(
                emojis=[emoji1, emoji2],
                result_url=str(response.url),
                result_data=response.content,
            )

        return None

    @staticmethod
    async def _request_mashup(client: httpx.AsyncClient, url: str, pool: AsyncPool) -> httpx.Response | None:
        response = await client.get(url)
        print(url, response.status_code)
        if response.status_code == 200:
            pool.stop = True
            return response
        return None
