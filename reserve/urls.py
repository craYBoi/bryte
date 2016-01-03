from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

# from .views import ReserveView


urlpatterns = [
    url(r'^$', 'reserve.views.reserve', name='reserve'),
    url(r'^success/', 'reserve.views.success', name='reserve_success'),
]