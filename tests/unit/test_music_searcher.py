from app.core.services import MusicSearcher


def test_add_new_searcher(fake_music):
    music_searcher = MusicSearcher(fake_music)
    music_searcher[1]('query')
    assert type(music_searcher[1].next()) is list


def test_next_for_searcher_without_query(fake_music):
    music_searcher = MusicSearcher(fake_music)
    assert music_searcher[2].next() == []


def test_prev_for_searcher_without_query(fake_music):
    music_searcher = MusicSearcher(fake_music)
    assert music_searcher[3].next() == []
