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

	# for filter
	def get_queryset(self, *args, **kwargs):
		qs = super(PhotographerListView, self).get_queryset(*args, **kwargs)
		query = self.request.GET.get('q')
		keyword = self.request.GET.get('k')
		if query:
			qs = self.model.objects.filter(
					Q(last_name__icontains = query) |
					Q(first_name__icontains = query)
				)
		if keyword:
			if keyword == 'student':
				qs = self.model.objects.filter(Q(is_student=True))
			elif keyword == 'pro':
				qs = self.model.objects.filter(~Q(is_student=True))
			else:
				qs = self.model.objects.all()
		return qs



def PhotographerDetailViewF(request, slug):
	photographer = Photographer.objects.get(slug=slug)

	# static url for 5 star rating
	total_rating = photographer.total_rating
	rating_static_url = 'img/' + str(total_rating) + 'star.png'
	ratings = photographer.rating_set.all()
	has_rating = True
	if not ratings:
		has_rating = False

	comment_ratings = ['img/'+str(ra.rating)+'star.png' for ra in ratings]

	# bootstrap col width
	num_of_feature = len(photographer.package_set.all())
	col_num = ceil(num_of_feature/float(3))
	last_col_width = num_of_feature%3
	if last_col_width == 0:
		last_col_width = 3

	col_url = 'col-sm-' + str(12/last_col_width)


	# check if the user is our user for now
	# will use @login_required later, and create seperate comment app
	permission = False
	if request.user.is_authenticated():
		reservations = Reservation.objects.filter(complete=True)
		if request.user.profile in [pur.profile for pur in reservations]:
			permission = True


	# process the rating form
	rating_form = RatingForm(request.POST or None)
	if rating_form.is_valid():
		instance = rating_form.save(commit=False)
		instance.photographer = photographer
		instance.save()
		return redirect(photographer.get_absolute_url())


	context = {}
	context['rating_static_url'] = rating_static_url
	context['ratings'] = zip(comment_ratings, ratings)
	context['rating_form'] = rating_form
	context['title_text'] = photographer.first_name + ' ' + photographer.last_name
	context['col_url'] = col_url
	context['has_rating'] = has_rating	
	context['object'] = photographer
	context['page_url'] = 'http://www.brytephoto.com' + str(photographer.get_absolute_url())
	context['permission'] = permission

	return render(request, 'photographer/photographer_detail.html', context)