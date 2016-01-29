from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import reserve, reserve_detail, success, checkout

urlpatterns = [
    url(r'^$', reserve, name='reserve'),
    url(r'^checkout/$', checkout, name='reserve_checkout'),
    url(r'^success/$', success, name='reserve_success'),
    url(r'^(?P<slug>[\w-]+)/$', reserve_detail, name='reserve_detail'),
    # url(r'^(?P<name>[a-z ]+)/$', 'reserve.views.reserve_specific', name='reserve_specific'),
]