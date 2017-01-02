import os.path
from base import BaseView
from django.contrib.auth import authenticate, login
from music.services.config import ConfigService
from music.services.song import SongService


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

        home_dir = "/home/jmg"
        config = ConfigService().get_or_new(id=1)
        return self.render_to_response({"home_dir": home_dir, "config": config})


class LoadSongsView(BaseView):

    def post(self, *args, **kwargs):

        directory = self.request.POST.get("directory")
        songs = ConfigService().save_songs_for_dir(directory)

        return self.json_response({"count": len(songs)})


class SaveConfigView(BaseView):

    def post(self, *args, **kwargs):

        ConfigService().save(self.request.POST)

        return self.json_response({"status": "ok"})


class DeleteAllSongsView(BaseView):

    def post(self, *args, **kwargs):

        for song in SongService().all():
            song.delete()

        return self.json_response({"status": "ok"})