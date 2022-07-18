from app.core.loader import music
from app.core.services import MusicSearcher

searcher = MusicSearcher(music, 7, 5)
local_searcher = MusicSearcher(step=7, pages=5, local=True)
