from django.shortcuts import render

from .forms import SignUpForm
from photographer.models import Photographer
from .models import Price, PriceFeature

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


def safety(request):
	context = {
		'title_text': 'safety',
	}

	return render(request, "safety.html", context)


def pricing(request):
	pro_prices = Price.objects.filter(is_student=False)
	student_prices = Price.objects.filter(is_student=True)
	context = {
		'title_text': 'pricing',
		'pro_prices': pro_prices,
		'student_prices': student_prices,
	}

	return render(request, "pricing.html", context)


def student_hs(request):
	student_prices = Price.objects.filter(is_student=True)
	context = {
		'title_text': 'student headshot',
		'student_prices': student_prices,
	}

	return render(request, 'student_hs.html', context)


def pro_hs(request):
	pro_prices = Price.objects.filter(is_student=False)
	context = {
		'title_text': 'professional headshot',
		'pro_prices': pro_prices,
	}

	return render(request, 'pro_hs.html', context)


def group_hs(request):
	context = {
		'title_text': 'group headshot',
	}

	return render(request, 'group_hs.html', context)










