from app.core.services.search import MusicSearcher


def test_search_anything(fake_music):
    searcher = MusicSearcher(music=fake_music, step=5, pages=5)
    searcher[88]('anything')
    assert len(searcher[88].next()) == 5
    assert len(searcher[88].prev()) == 5


def test_search_without_query(fake_music):
    searcher = MusicSearcher(music=fake_music, step=5, pages=5)
    assert len(searcher[99].next()) == 0
    assert searcher[99].prev() == []
    assert searcher[99].next() == []
    assert len(searcher[99].prev()) == 0


def test_search_step(fake_music):
    searcher1 = MusicSearcher(music=fake_music, step=3, pages=5)
    searcher1[12]('anything')
    assert len(searcher1[12].next()) == 3
    searcher2 = MusicSearcher(music=fake_music, step=30, pages=5)
    searcher2[22]('anything')
    assert len(searcher2[22].next()) == 30
