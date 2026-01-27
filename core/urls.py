from django.urls import path,include,re_path
from .consumers import EchoConsumer
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, GetUsersView, GetCurrentUserView

urlpatterns = [
    path('login/', obtain_auth_token),
    path("signup/", RegisterView.as_view()),
    path("users/", GetUsersView.as_view()),
    path("me/", GetCurrentUserView.as_view()),
]

websocket_urlpatterns = [
    re_path(r"ws/", EchoConsumer.as_asgi()),
]