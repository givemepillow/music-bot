import asyncio


class BackrefLock(asyncio.Lock):
    def __init__(self, lock_table, *args, **kwargs):
        super(BackrefLock, self).__init__(*args, **kwargs)
        self._lock_table = lock_table
        self._key = None

    def update_key(self, key: int):
        self._key = key
        return self

    def remove_key(self):
        self._key = None
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super(BackrefLock, self).__aexit__(exc_type, exc_val, exc_tb)
        del self._lock_table[self._key]


class LockTable:

    def __init__(self, locks_number: int = 7):
        self.pool = asyncio.queues.Queue()
        for _ in range(locks_number):
            self.pool.put_nowait(BackrefLock(self))
        self.locks = dict()
        self.links_count = dict()

    async def __call__(self, key: int) -> asyncio.Lock:
        if key not in self.locks:
            self.locks[key] = (await self.pool.get()).update_key(key)
            self.links_count[key] = 0
        self.links_count[key] += 1
        return self.locks[key]

    def __delitem__(self, key):
        self.links_count[key] -= 1
        if self.links_count[key] == 0:
            self.pool.put_nowait(self.locks[key].remove_key())
            del self.locks[key]
            del self.links_count[key]

    def __contains__(self, item):
        return item in self.locks
