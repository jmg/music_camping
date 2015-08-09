from django.conf.urls import patterns, include, url
from django_conventions import UrlsManager
import music.views as views_root

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
)

UrlsManager(urlpatterns, views_root)
