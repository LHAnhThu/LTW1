from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>\w+)/(?P<other_username>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
