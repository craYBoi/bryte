from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

# Create your views here.

from .models import Photographer
from .forms import RatingForm
from reserve.models import Reservation

class PhotographerListView(ListView):
	model = Photographer
	template_name = 'photographer_list.html'

	def get_context_data(self, *args, **kwargs):
		# reset title
		context = super(PhotographerListView, self).get_context_data(*args, **kwargs)
		context['title_text'] = 'Photographers'
		return context
	# queryset = Photographer.objects.all()
	# template_name = 'photographer/photographer_list.html'


class PhotographerDetailView(DetailView):
	model = Photographer
	form_class = RatingForm
	
	def get_context_data(self, *args, **kwargs):
		# reset title
		context = super(PhotographerDetailView, self).get_context_data(*args, **kwargs)
		photographer = self.get_object()
		rating_form = RatingForm()
		context['rating_form'] = rating_form
		context['title_text'] = photographer.first_name + ' ' + photographer.last_name
		return context

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST or None)
		if form.is_valid():
			instance = form.save(commit=False)
			photographer = self.get_object()
			instance.photographer = photographer
			instance.save()
			return redirect(photographer.get_absolute_url())
		print 'Error dealing post data'
