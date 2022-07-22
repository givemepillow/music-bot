import asyncio


class LockTable:

    def __init__(self):
        self.locks = dict()
        self.links_count = dict()

    def __getitem__(self, key: int) -> asyncio.Lock:
        if key not in self.locks:
            self[key] = asyncio.Lock()
        return self.locks[key]

    def __setitem__(self, key: int, value: asyncio.Lock) -> None:
        if value not in self.locks:
            self.links_count[key] = 1
            self.locks[key] = value
        else:
            self.links_count[key] += 1

    def __delitem__(self, key):
        self.links_count[key] -= 1
        if self.links_count == 0:
            del self.locks[key]

    def __contains__(self, item):
        return item in self.locks

    def __len__(self):
        return len(self.locks)
