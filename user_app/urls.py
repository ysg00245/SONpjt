from django.conf.urls import url
from user_app import views

urlpatterns = [
    url(r'^$'      , views.null , name = "null"),
    url(r'^login', views.login, name = "login"),
    url(r'^info', views.info, name = "info"),
    url(r'^inven', views.inven, name = "inven")
]
