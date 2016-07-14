from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Timeslot, Booking, Signup, Nextshoot

import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# School url definition
# brown -> Brown University
# ric -> Rhode Island College
# bu -> Boston University
# bc -> Boston College
# ccri -> Community College of Rhode Island


def index(request, school='brown'):

	context = {
		'brown_careerlab': 1,
	}
	timeslots = ''
	nextshoot = ''
	title = ''
	bg_url = ''
	logo_url = ''
	school_name = ''
	school_url = ''
	school_bryte_url = ''
	school_title = ''
	school_location = ''
	school_year_choices = ['<25% of credits completed', '25-50% of credits completed', '50-75% of credits completed', '>75% of credits completed']
	area_of_study_choices = ['Biological/Medicinal Sciences', 'Nursing', 'Human Services', 'Psychology', 'Physical Sciences', 'Computer Science', 'Mathematics and Statistics', 'English/Literature', 'History', 'Sociology', 'Education', 'Environmental Sciences', 'Public Administration/Social Services', 'Business/Management', 'Marketing/Communications', 'Economics/Finance', 'Visual and Performing Arts', 'Journalism']
	professional_path_choices = ['Business Administration/Management', 'Social Services and Nonprofits', 'Government', 'Education', 'Personal Care and Other Services', 'Marketing', 'Sales and Related', 'Healthcare, Pharmaceuticals', 'Finance, Insurance', 'Real Estate', 'Computer Engineering/IT', 'Architecture', 'Freelance Artist', 'Legal', 'Media/Journalism', 'Sports and Physical Fitness']
	modal_form_title = ''

	# view logic for different schools here
	# filter by the school name and pick the first
	if school.lower() == 'brown':
		title = 'Bryte & CareerLab Brown University Headshot'
		nextshoot = Nextshoot.objects.filter(school='Brown University')
		bg_url = static('img/brown_campus.jpg')
		logo_url = static('logo/brown_logo.png')
		school_name = 'Brown University CareerLAB'
		school_url = 'http://www.brown.edu'
		school_bryte_url = 'brown'
		school_title = 'CareerLAB'
		school_location = 'Brown CareerLAB, 167 Angell St'
		modal_form_title = 'Brown Form Title'
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404

	elif school.lower() == 'bu':
		title = 'Bryte & Boston University Headshot'
		nextshoot = Nextshoot.objects.filter(school='Boston University')
		bg_url = static('img/bu/bg.jpg')
		logo_url = static('img/bu/logo.png')
		school_name = 'Boston University Feld Career Center'
		school_url = 'http://www.bu.edu'
		school_title = 'BU Career Center'
		school_bryte_url = 'bu'
		school_location = 'Feld Career Center, 595 Commonwealth Ave.'
		modal_form_title = 'BU Form title'
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404


	elif school.lower() == 'ccriknight':
		title = 'Bryte & the Community College of Rhode Island Knight Campus Headshot'
		bg_url = static('img/ccri/bg.JPG')
		logo_url = static('img/ccri/logo.png')
		school_name = 'Community College of Rhode Island'
		school_url = 'http://www.ccri.edu'
		school_bryte_url = 'ccriknight'
		school_title = 'Career Planning'
		school_location = 'Great Hall just outside the Career Planning Office'
		modal_form_title = 'Thank you for helping Bryte and Career Planning better engage with CCRI students'
		nextshoot = Nextshoot.objects.filter(school='Community College of Rhode Island')
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404

	elif school.lower() == 'bu':
		title = 'Bryte & Boston University of Rhode Island Headshot'
		bg_url = static('img/ccri/bg.jpg')
		logo_url = static('img/ccri/logo.png')
		school_name = 'Boston University'
		school_url = 'http://www.ccri.edu'
		nextshoot = Nextshoot.objects.filter(school='Boston University')
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404

	else:
		raise Http404


	context['title_text'] = title
	context['timeslots'] = timeslots
	context['next_shoot'] = nextshoot
	context['logo_url'] = logo_url
	context['bg_url'] = bg_url
	context['school_url'] = school_url
	context['school_name'] = school_name
	context['school_title'] = school_title
	context['school_bryte_url'] = school_bryte_url
	context['school_location'] = school_location
	context['school_year_choices'] = school_year_choices
	context['modal_form_title'] = modal_form_title
	context['professional_path_choices'] = sorted(professional_path_choices)
	context['area_of_study_choices'] = sorted(area_of_study_choices)

	# next_shoot = Nextshoot.objects.first()
	# timeslots = next_shoot.timeslot_set.filter(is_available=True, active=True).order_by('time')
	# timeslots = Timeslot.objects.filter(active=True, is_available=True).order_by('time')
	# if timeslots:
	# 	next_shoot = timeslots.first().shoot

	return render(request, 'careerlab_index.html', context)


def book(request):
	if request.is_ajax() and request.method == 'POST':

		data = {}

		email = request.POST.get('email')
		name = request.POST.get('name')
		school_year = request.POST.get('schoolyear')
		professional_path = request.POST.get('profession')
		area_of_study = request.POST.get('major')
		time_id = request.POST.get('time')
		timeslot = get_object_or_404(Timeslot, pk=time_id)
		shoot = timeslot.shoot
		emails = [e.email for elem in shoot.timeslot_set.all() for e in elem.booking_set.all()]

		# avoid duplicate booking
		if email in emails:
			data['msg'] = 'Looks like you have already booked a headshot. If you have not recieved a confirmation email, you will get one soon. We have you in the system :)<br>'		
		else:

			# increment the timeslot first to reduce confliction
			if timeslot.is_available:
				try:
					b = Booking.objects.create(
						email = email,
						name = name,
						timeslot = timeslot,
						program_progress = school_year,
						area_of_study = area_of_study,
						professional_path = professional_path,
						)
				except Exception, e:
					raise e
					data['msg'] = 'There\'s an error signing up. Please try again.'
				else:
					# delete record in the signup list
					if email in [signup.email for signup in Signup.objects.all()]:
						try:
							signup = get_object_or_404(Signup, email=email)
						except Exception, e:
							print e
							pass
						else:
							signup.delete()

					# send email
					b.booking_confirmation_email()
					first_name = name.split(' ')[0]
					data['msg'] = 'Thanks for signing up ' + first_name + '.<br><br>A confirmation email will be sent to you at \"' + str(email) + '\" with your booking information soon!<br><br>Team Bryte'

			else:
				data['msg'] = 'This time slot is no longer available. Please select a different one.'


		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


def signup(request):
	if request.is_ajax() and request.method == 'POST':

		email = request.POST.get('email')
		name = request.POST.get('name')
		shoot_pk = request.POST.get('shoot')
		school_year = request.POST.get('schoolyear')
		professional_path = request.POST.get('profession')
		major = request.POST.get('major')

		print shoot_pk

		data = {}

		# avoid duplicate signup
		if email in [signup.email for signup in Signup.objects.all()]:
			data['msg'] = 'It seems that you have already signed up!<br>We will notify at ' + str(email) + ' whenever next headshot session is available!<br><br>Thanks!<br>Team Bryte'
		else:
			# get the first shooting instance
			shoot = get_object_or_404(Nextshoot, pk=shoot_pk)
			try:
				s = Signup.objects.create(
					email = email,
					name = name,
					shoot = shoot,
					program_progress = school_year,
					area_of_study = major,
					professional_path = professional_path,
					)
			except Exception, e:
				print e
				data['msg'] = 'There\'s an error signing up. Please try again.'
				pass
			else:
				first_name = name.split(' ')[0]
				data['msg'] = 'Thanks for signing up ' + str(first_name) + '. We will notify you for the next headshot session!<br><br>Team Bryte'

		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404

# could subject to change to Shoot school name
def cancel_order(request):
	context = {
		'brown_careerlab': 1,
		'title_text': 'Cancel your signup'
	}
	if request.method == 'GET':
		order_id = request.GET.get('order_id')
		try:
			booking = get_object_or_404(Booking, hash_id=order_id)
		except Exception, e:
			pass
		else:
			name = booking.name
			email = booking.email
			timeslot = booking.timeslot
			shoot = timeslot.shoot
			first_name = name.split(' ')[0]

			# generate the correct booking url in email
			url = ''
			if shoot.school == 'Community College of Rhode Island':
				url = 'www.brytephoto.com/school/ccriknight'
			else:
				url = ''

			booking.cancel_order()
			msg_body = 'Hi ' + str(first_name) + ',\n\nThis email is to confirm you have cancelled your Bryte Photo headshot on ' + str(booking.timeslot) + '. If you would like to book a different time slot you can sign up here:\n\n'+ url +'\n\nBest,\nTeam Bryte'
			try:
				send_mail('Cancellation confirmation - Bryte Photo',
					msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [email],
					fail_silently=False)
			except Exception, e:
				print 'Email not sent'
				pass

	return render(request, 'notification.html', context)


def tips(request):
	context = {
		'brown_careerlab': 1,
		'title_text': 'Bryte Photo Headshot Tips',
	}
	return render(request, 'careerlab_tips.html', context)



def pay(request):
	context = {
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
		'title_text': 'Checkout at Bryte Photo',
	}
	if request.method == 'POST':
		token = request.POST.get('stripeToken')
				# charge
		try:
			charge = stripe.Charge.create(
				amount = 1199,
				currency="usd",
				source=token,
				description="Bryte Passport Photo"
			)
		except stripe.error.CardError, e:
			print e
			data = {'successMsg': 'There\'s an error charging your card. Please provide another card',}
			return HttpResponse(json.dumps(data), content_type='application/json')
		else:
			context['notify'] = 'Thanks! You have successfully paid! Thanks for using Bryte!'

	return render(request, 'careerlab_pay.html', context)