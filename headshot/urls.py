from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import student_hs, pro_hs, group_hs, hs

urlpatterns = [
	url(r'^$', hs, name='main_hs'),
	url(r'^student/$', hs, name='student_hs'),
	url(r'^pro/$', hs, name='pro_hs'),
	url(r'^group/$', hs, name='group_hs'),
] 