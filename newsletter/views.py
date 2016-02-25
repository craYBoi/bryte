from django.shortcuts import render
from django.conf import settings


from .forms import SignUpForm
from photographer.models import Photographer
from .models import Price, PriceFeature

# Create your views here.
def home(request):
	form = SignUpForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		# print instance
		instance.save()

	title = 'Welcome'

	# featured photographer

	photographer_qs = Photographer.objects.filter(is_featured=True)
	featured_pg = photographer_qs[:2]

	featured_pg_one = featured_pg[0]
	featured_pg_two = featured_pg[1]
	featured_pg_one_vid = featured_pg_one.photographervideo_set.all()[1]
	featured_pg_two_vid = featured_pg_two.photographervideo_set.all()[0]
	context = {
		'signUp': form,
		'title': title,
		'featured_pg_one': featured_pg_one,
		'featured_pg_two': featured_pg_two,
		'featured_pg_one_vid': featured_pg_one_vid,
		'featured_pg_two_vid': featured_pg_two_vid,
		'title_text': 'Bryte',
	}
	return render(request, "index.html", context)


def about(request):
	context = {
		'title_text': 'about',
	}

	return render(request, "about.html", context)


def package(request):
	# filter get request to get price packages
	packages = Price.objects.all().order_by('price')
	if request.method == "GET":
		photo_video = request.GET.get('photo_video')
		re_sb = request.GET.get('re_sb')

		is_photo = False
		print photo_video
		if photo_video and re_sb:
			if photo_video=='photography':
				is_photo = True
			
			packages = Price.objects.filter(is_photography=is_photo).order_by('price')
			packages = packages.filter(category=re_sb).order_by('price')


	# create a list of a list of packages
	# 0 - House Tour, 1 - Advertising Video, 2 - Promotional Video
	# 3 - House Photo, 4 - Small Business Marketing Photo, 5 - Product Photo
	list_of_packages = {}
	for package in packages:
		if package.shared_title in list_of_packages:
			list_of_packages[package.shared_title].append(package)
		else:
			list_of_packages[package.shared_title] = [package]


	context = {
		'title_text': 'Packages',
		'packages': packages,
		'packages_list': list_of_packages,
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


def get_started(request):
	context = {
		'title_text': 'Get Started'
	}
	return render(request, 'get_started.html', context)


def legal(request):
	context = {
		'title_text': 'Legal Documentations'
	}

	return render(request, 'legal_stuff.html', context)
