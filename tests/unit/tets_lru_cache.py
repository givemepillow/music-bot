from app.core.services import LRUCache


def test_cache_size():
    cache = LRUCache(capacity=128)
    for i in range(128):
        cache[i] = i
    assert (128 not in cache) is True
    assert (127 in cache) is True
    cache[129] = 129
    assert (63 not in cache) is True
    assert (64 in cache) is True
    assert (127 in cache) is True
    assert (129 in cache) is True
