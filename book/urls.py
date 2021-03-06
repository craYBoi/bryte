from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import checkout, signup, pay

urlpatterns = [
	url(r'^$', checkout, name='book_checkout'),
	url(r'^signup$', signup, name='book_signup'),
	url(r'^pay$', pay, name='book_pay')
]