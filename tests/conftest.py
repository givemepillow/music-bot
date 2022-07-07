import pytest
from aiovkmusic import Track


class FakeMusic:
    """
    Фейковый класс частично имитирующий работу класса Music
    из пакета aiovkmusic.
    """
    results = []

    def search(self, text, count, *args, **kwargs):
        self.results.clear()
        for i in range(count):
            self.results.append(
                Track(
                    id=999999999,
                    owner_id=999999999,
                    artist='Artist',
                    title=text,
                    duration=300,
                    _covers=[],
                    url='url'
                )
            )
        return self.results


@pytest.fixture()
def fake_music():
    return FakeMusic()
