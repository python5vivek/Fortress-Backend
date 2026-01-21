from django.urls import path,include,re_path
from .consumers import EchoConsumer

urlpatterns = [

]

websocket_urlpatterns = [
    re_path(r"ws/", EchoConsumer.as_asgi()),
]