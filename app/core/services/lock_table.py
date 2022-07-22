import asyncio


class BackrefLock(asyncio.Lock):
    def __init__(self, key, table, *args, **kwargs):
        super(BackrefLock, self).__init__(*args, **kwargs)
        self.key = key
        self.table = table

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super(BackrefLock, self).__aexit__(exc_type, exc_val, exc_tb)
        del self.table[self.key]


class LockTable:

    def __init__(self):
        self.locks = dict()
        self.links_count = dict()

    def __call__(self, key: int):
        return self.__getitem__(key)

    def __getitem__(self, key: int) -> asyncio.Lock:
        if key not in self.locks:
            self.locks[key] = BackrefLock(key, self)
            self.links_count[key] = 0
        self.links_count[key] += 1
        return self.locks[key]

    def __delitem__(self, key):
        self.links_count[key] -= 1
        if self.links_count[key] == 0:
            del self.locks[key]
            del self.links_count[key]

    def __contains__(self, item):
        return item in self.locks
