"""
Модуль для кэширования данных.
"""

from collections import OrderedDict


class LRUCache:
    """
    Данный класс представляет собой простую реализацию LRU-кэша,
    где в начале находят уже давно не используемые элементы,
    а в конце - недавно использованные.
    """

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def __getitem__(self, key: int) -> int:
        """
        При получении элемента, передвигаем его в конец.
        """
        self.cache.move_to_end(key)
        return self.cache[key]

    def __setitem__(self, key: int, value: int) -> None:
        """
        При сохранении элемента, также передвигаем его в конец.
        Если элементов больше вместимости - удаляем половину от начала.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            for _ in range(self.capacity // 2):
                self.cache.popitem(last=False)

    def __contains__(self, item):
        return item in self.cache

    def __len__(self):
        return len(self.cache)
