from .mashup_interface import MashupInterface
from .mashup_google import GoogleMashup
from ..settings import MainSettings


def init_mashupers():
    GoogleMashup(MainSettings.get().mashupers.google).set_this()


def mashuper() -> MashupInterface:
    return GoogleMashup.get()
