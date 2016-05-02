from django.conf import settings
from django.conf.urls import include, url

from .views import index, book, signup

urlpatterns = [
	url(r'^$', index, name='careerlab_index'),
	url(r'^book$', book, name='careerlab_book'),
	url(r'^signup$', signup, name='careerlab_signup'),

]