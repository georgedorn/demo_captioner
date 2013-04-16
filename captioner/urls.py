from django.conf.urls import patterns, url

from .views import CreateStory, ViewStory
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^(?P<assignment>.+)/story/$', login_required(CreateStory.as_view()), name='create_story'),
    url(r'^/story/(?P<pk>.+)/$', login_required(ViewStory.as_view()), name='view_story'),
)
