from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.db.models import Q
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

# Create your views here.

from .models import Photographer
from .forms import RatingForm
from reserve.models import Reservation

from math import ceil

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

		# static url for 5 star ratings
		total_rating = photographer.total_rating
		rating_static_url = 'img/' + str(total_rating) + 'star.png'
		ratings = photographer.rating_set.all()
		comment_ratings = ['img/'+str(ra.rating)+'star.png' for ra in ratings]

		# bootstrap col width
		num_of_feature = len(photographer.package_set.all())
		col_num = ceil(num_of_feature/float(3))
		last_col_width = num_of_feature%3
		if last_col_width == 0:
			last_col_width = 3

		col_url = 'col-sm-' + str(12/last_col_width)



		context['rating_static_url'] = rating_static_url
		context['ratings'] = zip(comment_ratings, ratings)
		context['rating_form'] = rating_form
		context['title_text'] = photographer.first_name + ' ' + photographer.last_name
		context['col_url'] = col_url
		return context

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST or None)
		if form.is_valid():
			instance = form.save(commit=False)
			photographer = self.get_object()
			instance.photographer = photographer

			# add validation of email if email in reservation.emails() then proceed, otherwise don't

			instance.save()
			return redirect(photographer.get_absolute_url())
		# context = self.get_context_data
		context = {}
		return render_to_response('photographer/photographer_detail.html', context)
