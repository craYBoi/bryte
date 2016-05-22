from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Timeslot, Booking, Signup

import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
	title = 'Bryte Photo & CareerLab Brown University headshot'
	timeslots = Timeslot.objects.filter(active=True, is_available=True).order_by('time')
	context = {
		'title_text': title,
		'timeslots': timeslots,
		'brown_careerlab': 1,
	}
	return render(request, 'careerlab_index.html', context)


def book(request):
	if request.is_ajax() and request.method == 'POST':

		data = {}

		email = request.POST.get('email')
		name = request.POST.get('name')

		time_id = request.POST.get('time')
		timeslot = get_object_or_404(Timeslot, pk=time_id)

		# increment the timeslot first to reduce confliction
		if timeslot.is_available:
			timeslot.increment()
			try:
				b = Booking.objects.create(
					email = email,
					name = name,
					timeslot = timeslot,
					)
			except Exception, e:
				print e
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
				b.confirmation_email()

				data['msg'] = 'Thanks for signing up ' + str(name) + '.<br><br>A confirmation email will be sent to you at \"' + str(email) + '\" with your booking information soon!<br><br>Team Bryte Photo'

		else:
			data['msg'] = 'This time slot is no longer available. Please select a different one.'


		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


def signup(request):
	if request.is_ajax() and request.method == 'POST':

		email = request.POST.get('email')
		name = request.POST.get('name')
		data = {}

		if email in [signup.email for signup in Signup.objects.all()]:
			data['msg'] = 'You have already signed up!<br>We will notify at ' + str(email) + ' whenever next headshot session is available!<br><br>Thanks!<br>Team Bryte Photo'
		else:
			try:
				s = Signup.objects.create(
					email = email,
					name = name,
					)
			except Exception, e:
				print e
				data['msg'] = 'There\'s an error signing up. Please try again.'
			else:
				data['msg'] = 'Thanks for signing up ' + str(name) + '. We will notify you for the next headshot session!<br><br>Team Bryte Photo'

		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


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
			booking.cancel_order()
			msg_body = 'Hi ' + str(name) + ',\n\nThis email is to confirm you have cancelled your Bryte Photo headshot on ' + str(booking.timeslot) + '. If you would like to book a different time slot you can sign up here:\n\nwww.brytephoto.com/CareerLAB\n\nBest,\nBryte Photo Team'
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
		'brown_careerlab': 1,
		'title_text': 'Bryte Photo Headshot Pay',	
	}
	return render(request, 'careerlab_pay.html', context)


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
				amount = 37400,
				currency="usd",
				source=token,
				description="Bryte Photo Photography"
			)
		except stripe.error.CardError, e:
			print e
			data = {'successMsg': 'There\'s an error charging your card. Please provide another card',}
			return HttpResponse(json.dumps(data), content_type='application/json')
		else:
			context['notify'] = 'Thanks! You have successfully paid! Thanks for using Bryte!'

	return render(request, 'careerlab_pay.html', context)