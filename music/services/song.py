from music.services.base import BaseService
from music.models import Song


class SongService(BaseService):

    entity = Song