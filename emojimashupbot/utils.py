import datetime
from typing import TypeVar, Type

T = TypeVar('T')


def get_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


class Singleton:

    @classmethod
    def get(cls: Type[T]) -> T:
        return cls._instance

    @classmethod
    def set(cls: Type[T], instance: T):
        cls._instance = instance

    def set_this(self: T) -> T:
        self.set(self)
        return self
