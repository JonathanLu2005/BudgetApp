from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
path("", views.SignUp, name="SignUp"),
path("Login/", views.Login, name="Login"),

path("Home/", views.Home, name="Home"),

path("Comparison/", views.Comparison, name="Comparison"),
]

urlpatterns += staticfiles_urlpatterns()