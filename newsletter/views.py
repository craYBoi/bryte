from django.shortcuts import render

from .forms import SignUpForm
from photographer.models import Photographer
# Create your views here.
def home(request):
	# print request.POST

	form = SignUpForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		# print instance
		instance.save()

	title = 'Welcome'

	# featured photographer
	num_of_featured = 3
	photographer_qs = Photographer.objects.all()
	if photographer_qs.count <= num_of_featured:
		featured_pg = photographer_qs.order_by('?')
	else:
		featured_pg = photographer_qs.order_by('?')[:num_of_featured]

	context = {
		'signUp': form,
		'title': title,
		'featured_pg': featured_pg,
		'title_text': 'Bryte',
	}
	return render(request, "index.html", context)


def about(request):
	context = {
		'title_text': 'about',
	}

	return render(request, "about.html", context)