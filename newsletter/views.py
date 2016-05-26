from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, HttpResponse

import stripe

import json
from .forms import SignUpForm
from photographer.models import Photographer
from .models import Price, PriceFeature, ContactSale, ContactHelp
from book.models import TimeSlot, NextShoot


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
	form = SignUpForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		# print instance
		instance.save()

	title = 'Bryte Photo | Custom and friendly headshot photography sessions for $20'

	timeslots = TimeSlot.objects.filter(is_available=True).order_by('time')
	next_shoot = NextShoot.objects.first()


	context = {
		'timeslots': timeslots,
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
		'title_text': title,
		'next_shoot': next_shoot,
		'is_index': 1,
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


def legal(request):
	context = {
		'title_text': 'Legal Documentations'
	}

	return render(request, 'legal_stuff.html', context)



def clients(request):
	context = {
		'title_text': 'Our Clients | Bryte Photo Headshots',
		'is_clients': 1,
	}
	return render(request, 'landing_clients.html', context)


def contact(request):
	context = {
		'title_text': 'Contact Sales | Bryte Photo Headshots',
		'is_contact': 1,
	}
	return render(request, 'landing_contact.html', context)


def help(request):
	context = {
		'title_text': 'Contact Help | Bryte Photo Headshots',
		'is_contact': 1,
	}
	return render(request, 'landing_help.html', context)


def ajax_contact(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		name = request.POST.get('name')
		email = request.POST.get('email')
		category = request.POST.get('category')
		org_name = request.POST.get('orgname')
		amount = request.POST.get('amount')
		question = request.POST.get('question')

		first_name = name.strip().split(' ')[0]

		# create database instance
		try:
			c = ContactSale.objects.create(name=name, email=email,category=category, organization=org_name, amount=amount,question=question)
		except Exception, e:
			print 'Fail to create instance'
			data['msg'] = 'There\'s an error signing up. Please try again.'
			raise e
		else:
			# send the email
			data['msg'] = 'Thank you ' + first_name + ' for contacting us! We will get to you as soon as we can!'

			msg_body = 'Contact Sales Information:\n\nName: ' + str(name) + '\nEmail: ' + str(email) + '\nOrganization: ' + str(org_name) + '\nCategory: ' + str(category) + '\nAmount of Headshots Estimate: ' + str(amount) + '\nQuestion & Request: ' + str(question) + '\n\nBest,\nBryte Photo Team'

			try:
				send_mail('New Contact Sales Inquiry!', msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [settings.EMAIL_HOST_USER], fail_silently=False)
			except Exception, e:
				print 'Email Not Sent!'
				raise e

		return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_help(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		name = request.POST.get('name')
		email = request.POST.get('email')
		question = request.POST.get('question')

		first_name = name.strip().split(' ')[0]

		# create database instance
		try:
			c = ContactHelp.objects.create(name=name, email=email, question=question)
		except Exception, e:
			print 'Fail to create instance'
			data['msg'] = 'There\'s an error signing up. Please try again.'
			raise e
		else:
			# send the message
			data['msg'] = 'Thank you ' + first_name + ' for contacting us! We will get to you as soon as we can!'

			msg_body = 'Contact Help Information:\n\nName: ' + str(name) + '\nEmail: ' + str(email) + '\nQuestion & Request: ' + str(question) + '\n\nBest,\nBryte Photo Team'

			# send the email
			try:
				send_mail('New Contact Help!', msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [settings.EMAIL_HOST_USER], fail_silently=False)
			except Exception, e:
				print 'Email Not Sent!'
				raise e

		return HttpResponse(json.dumps(data), content_type='application/json')