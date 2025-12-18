import random
import httpx
from .mashup_interface import MashupInterface
from ..models import Emoji, EmojiMashupResultComplete
from ..settings import MashupersSettings
from ..utils import Singleton


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

        async with httpx.AsyncClient() as client:
            random.shuffle(urls)
            for url in urls:
                    response = await client.get(url)
                    print(url, response.status_code)
                    if response.status_code == 200:
                        return EmojiMashupResultComplete(
                            emojis=[emoji1, emoji2],
                            result_url=url,
                            result_data=response.content,
                        )

        return None
