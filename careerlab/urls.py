from django.conf import settings
from django.conf.urls import include, url

from .views import index, book, signup, cancel_order, tips, pay, sales

urlpatterns = [
	url(r'^$', index, name='careerlab_index'),
	url(r'^book$', book, name='careerlab_book'),
	url(r'^signup$', signup, name='careerlab_signup'),
	url(r'^cancel$', cancel_order, name='careerlab_cancel_order'),
	url(r'^tips$', tips, name='careerlab_tips'),
	url(r'^pay$', pay, name='careerlab_pay'),
	url(r'^sales$', sales, name='careerlab_sales'),
]