import pytest
from aiovkmusic import Track

from app.core.services.search import MusicSearcher


@pytest.mark.asyncio
async def test_search_anything(fake_music):
    searcher = MusicSearcher(music=fake_music, step=5, pages=5)
    await searcher[88]('anything')
    assert len(searcher[88].next()) == 5
    assert len(searcher[88].prev()) == 5


def test_search_without_query(fake_music):
    searcher = MusicSearcher(music=fake_music, step=5, pages=5)
    assert len(searcher[99].next()) == 0
    assert searcher[99].prev() == []
    assert searcher[99].next() == []
    assert len(searcher[99].prev()) == 0


@pytest.mark.asyncio
async def test_search_step(fake_music):
    searcher1 = MusicSearcher(music=fake_music, step=3, pages=5)
    await searcher1[12]('anything')
    assert len(searcher1[12].next()) == 3
    searcher2 = MusicSearcher(music=fake_music, step=30, pages=5)
    await searcher2[22]('anything')
    assert len(searcher2[22].next()) == 30


@pytest.mark.asyncio
async def test_search_history(fake_music):
    searcher = MusicSearcher(music=fake_music, step=3, pages=5)
    await searcher[100]('anything')
    assert len(searcher[100].next()) == 3
    assert type(searcher[100].track(999999999)) is Track
    with pytest.raises(KeyError):
        searcher[100].track(1000)
