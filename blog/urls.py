from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import BlogListView, BlogDetailView

urlpatterns = [
	url(r'^$', BlogListView.as_view(), name='blogs'),
	url(r'^(?P<slug>[\w-]+)/$', BlogDetailView, name='blog_detail'),
] 