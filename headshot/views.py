from django.shortcuts import render

# Create your views here.
from newsletter.models import Price
from photographer.models import Photographer


def hs(request):
	context = {
		'title_text': 'headshot',
	}

	return render(request, 'main_hs.html', context)
	

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