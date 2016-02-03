from django.shortcuts import render
from django.conf import settings


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
		'mix_token': settings.MIXPANEL_TOKEN,
	}
	return render(request, "index.html", context)


def about(request):
	context = {
		'title_text': 'about',
	}

	return render(request, "about.html", context)


def package(request):
	context = {
		'title_text': 'Packages',
	}

	return render(request, "package.html", context)


def pricing(request):
	student_prices = Price.objects.all()
	context = {
		'title_text': 'pricing',
		'student_prices': student_prices,
	}

	return render(request, "pricing.html", context)


def become_photographer(request):
	context = {
		'title_text': 'Become a Student Photographer'
	}

	return render(request, 'become_photographer.html', context)


def select_photographer(request):
	context = {
		'title_text': 'How do we select our photographers'
	}

	return render(request, 'select_photographer.html', context)

def faq(request):
	context = {
		'title_text': 'FAQs'
	}

	return render(request, 'faq.html', context)








