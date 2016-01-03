from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

# Create your views here.

from .models import Photographer

class PhotographerListView(ListView):
	model = Photographer
	template = 'photographer_list.html'

	def get_context_data(self, *args, **kwargs):
		# reset title
		context = super(PhotographerListView, self).get_context_data(*args, **kwargs)
		context['title_text'] = 'Photographers'
		return context
	# queryset = Photographer.objects.all()
	# template_name = 'photographer/photographer_list.html'


class PhotographerDetailView(DetailView):
	model = Photographer
	
	def get_context_data(self, *args, **kwargs):
		# reset title
		context = super(PhotographerDetailView, self).get_context_data(*args, **kwargs)
		photographer = self.get_object()
		context['title_text'] = photographer.first_name + ' ' + photographer.last_name
		return context
