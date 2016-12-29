import os.path
from base import BaseView
from django.contrib.auth import authenticate, login
from music.services.config import ConfigService


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

        home_dir = os.path.expanduser('~')
        return self.render_to_response({"home_dir": home_dir})


class LoadSongsView(BaseView):

    def post(self, *args, **kwargs):

        directory = self.request.POST.get("directory")
        songs = ConfigService().save_songs_for_dir(directory)

        return self.json_response({"count": len(songs)})

