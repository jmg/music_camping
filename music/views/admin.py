from base import BaseView
from django.contrib.auth import authenticate, login


class LoginView(BaseView):

    def post(self, *args, **kwargs):

        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            login(self.request, user)
            return self.redirect("/admin/panel/")

        context = {
            "error": "User or password incorrect."
        }

        return self.render_to_response(context)


class PanelView(BaseView):

    def get(self, *args, **kwargs):

        return self.render_to_response({})


class LoadView(BaseView):

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