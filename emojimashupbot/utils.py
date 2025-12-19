import asyncio
import datetime
from typing import TypeVar, Type, Generic, Coroutine

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


class AsyncPool(Generic[T]):
    def __init__(self, concurrency_limit: int):
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.tasks: list[Coroutine] = list()
        self.results: list[T|None] = list()
        self.stop = False

    def add_task(self, coro: Coroutine):
        self.tasks.append(coro)

    async def run(self):
        self.results = [None] * len(self.tasks)
        await asyncio.gather(*[self._run_one(i, coro) for i, coro in enumerate(self.tasks)])

    async def _run_one(self, idx: int, coro: Coroutine):
        async with self.semaphore:
            if not self.stop:
                self.results[idx] = await coro
