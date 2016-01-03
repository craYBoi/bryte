from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import PhotographerListView, PhotographerDetailView

urlpatterns = [
	url(r'^$', PhotographerListView.as_view(), name='photographers'),
	url(r'^(?P<slug>[\w-]+)/$', PhotographerDetailView.as_view(), name='photographer_detail'),
] 