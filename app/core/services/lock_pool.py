import asyncio


class BackrefLock(asyncio.Lock):
    """
    Класс унаследованный от asyncio.Lock c ссылкой на содержащий объект
    и двумя методами, позволяющими устанавливать и убирать
    ключ, по которому класс идентифицируется в содержащем объекте.
    """
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
        """
        При выходе из контекстного менеджера объект пробует удалить сам себя
        из содержащего объекта.
        """
        await super(BackrefLock, self).__aexit__(exc_type, exc_val, exc_tb)
        del self._lock_table[self._key]


class LockPool:
    """
    Класс-хранилище BackrefLock, используемых по ключу.
    Для каждого BackrefLock отслеживается количество ссылок.
    """
    def __init__(self, locks_number: int = 7):
        """
        Создаёт словарь, в котором по ключу будут храниться BackrefLock и
        ещё один словарь для подсчёта кол-во ссылок на BackrefLock.
        Кроме этого создаётся асинхронная очередь со свободными BackrefLock.
        :param locks_number: размер очереди.
        """
        self.pool = asyncio.queues.Queue()
        for _ in range(locks_number):
            self.pool.put_nowait(BackrefLock(self))
        self.locks = dict()
        self.links_count = dict()

    async def __call__(self, key: int) -> BackrefLock:
        """
        Возвращает свободный BackrefLock из очереди, если свободный нет,
        то блокируется до появления освободившегося.
        :param key: ключ по которому будет храниться BackrefLock на время использования.
        :return: BackrefLock
        """
        if key not in self.locks:
            self.locks[key] = (await self.pool.get()).update_key(key)
            self.links_count[key] = 0
        self.links_count[key] += 1
        return self.locks[key]

    def __delitem__(self, key):
        """
        Удаляет BackrefLock из используемых в данное время объектов если количество ссылок == 0.
        После удаления помещает BackrefLock обратно в асинхронную очередь.
        :param key:
        """
        self.links_count[key] -= 1
        if self.links_count[key] == 0:
            self.pool.put_nowait(self.locks[key].remove_key())
            del self.locks[key]
            del self.links_count[key]

    def __contains__(self, item):
        return item in self.locks
