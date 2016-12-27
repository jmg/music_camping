from base import BaseView

import os
import mimetypes
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from music.models import Song
from music.services.song import SongService
import eyeD3


class SongListView(BaseView):

    def get(self, *args, **kwargs):

        columnIndexNameMap = {
            0: 'name',
            1: 'album',
            2: 'artist',
            3: lambda song: self.render("song/actions.html", {"song": song })
        }
        sortIndexNameMap = {
            0: 'name',
            1: 'album',
            2: 'artist',
            3: None,
        }

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
