from django.conf import settings
from django.conf.urls import include, url

from .views import index, book, signup, cancel_order, tips, pay,order_feedback, checkin

urlpatterns = [
	url(r'^$', index, name='careerlab_index'),
	url(r'^book$', book, name='careerlab_book'),
	url(r'^signup$', signup, name='careerlab_signup'),
	url(r'^cancel$', cancel_order, name='careerlab_cancel_order'),
	url(r'^tips/$', tips, name='careerlab_tips'),
	url(r'^pay/$', pay, name='careerlab_pay'),
	url(r'^feedback/$', order_feedback, name='feedback_rating'),
	url(r'^(?P<school>[a-zA-Z]*)/$', index, name='careerlab_index'),
	url(r'^(?P<school>[a-zA-Z]*)/checkin$', checkin, name='careerlab_checkin'),
]