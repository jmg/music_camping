from base import BaseView

import os
import mimetypes
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from music.models import Song
from music.services.song import SongService
import eyed3


class SongListView(BaseView):

    def get(self, *args, **kwargs):

        columnIndexNameMap = { 0: 'name', 1: lambda song: self.render("song/actions.html", {"song": song }) }
        sortIndexNameMap = { 0: 'name' , 1: None, }

        return SongService().open_search(self.request, columnIndexNameMap, sortIndexNameMap)


class StreamView(BaseView):

    def get(self, *args, **kwargs):

        the_file = self.request.GET.get("filename")
        filename = os.path.basename(the_file)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(the_file), chunk_size),
                           content_type=mimetypes.guess_type(the_file)[0])
        response['Content-Length'] = os.path.getsize(the_file)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response


class LoadView(BaseView):

    def get(self, *args, **kwargs):

        return self.render_to_response({})

    def post(self, *args, **kwargs):

        directory = self.request.POST.get("directory")
        self.get_songs_for_dir(directory)
        return self.response("ok")

    def get_songs_for_dir(self, directory):

        songs = []
        for directory, sub_folders, files in os.walk(directory):
            for file in files:
                if self.valid_format(file):
                    path = os.path.join(directory, file)

                    tag = eyeD3.Tag()
                    tag.link(path)

                    song, _ = Song.objects.get_or_create(
                        path=path,
                        defaults={
                            "name": tag.getTitle(),
                            "artist": tag.getArtist(),
                            "album": tag.getAlbum(),
                        }
                    )
                    song.save()
                    songs.append(song)

        return songs

    def valid_format(self, name):

        validFormats = ['.mp3','.wav','.wma', '.avi', '.ogg']
        for format in validFormats:
            if name.find(format) != -1:
                return True
        return False