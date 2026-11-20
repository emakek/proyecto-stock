
from django.contrib import admin
from django.urls import path

from E_publica import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
]
