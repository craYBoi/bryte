from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404, HttpResponse

from .models import Book, TimeSlot, Signup
from photographer.models import Photographer

import json
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def signup(request):
	if request.is_ajax() and request.method == 'POST':

		email = request.POST.get('email')

		data = {}

		if email in [signup.email for signup in Signup.objects.all()]:
			data['successMsg'] = 'You have already signed up!<br>We will notify at ' + str(email) + ' whenever next headshot session is available!<br><br>Thanks!<br>Team Bryte Photo'
		else:
			signup_instance = Signup(email=email)
			signup_instance.save()

			data['successMsg'] = 'You have successfully signed up!<br>We will notify you at ' + str(email) + ' as soon as we schedule our next event. Looking forward to seeing you there!<br><br>Team Bryte Photo'
			
		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404



def checkout(request):
	if request.is_ajax() and request.method == 'POST':
		# print request.POST
		token = request.POST.get('token')
		name = request.POST.get('name')
		time_id = request.POST.get('time')
		time = get_object_or_404(TimeSlot, pk=time_id)
		email = request.POST.get('email')
		photographer_id = request.POST.get('photographer')
		photographer = get_object_or_404(Photographer, pk=photographer_id)

		data = {}

		# check for conflict before charging
		if not time.is_available:
			data = {
				'successMsg': 'The slot you chose is not available anymore..<br>Please choose another slot<br>Don\'t worry we didn\'t charge you<br><br>Team Bryte Photo',
			}
			return HttpResponse(json.dumps(data), content_type='application/json')


		# charge
		try:
			charge = stripe.Charge.create(
				amount = 2500,
				currency="usd",
				source=token,
				description="Bryte Photo Headshot"
			)
		except stripe.error.CardError, e:
			print e
			data = {'successMsg': 'There\'s an error charging your card. Please provide another card',}
			return HttpResponse(json.dumps(data), content_type='application/json')
		else:
			
			# change the availability
			time.is_available = False
			time.save()

			# add book instance
			book_instance = Book(
				photographer=photographer,
				name=name,
				email=email,
				timeslot=time,
				)
			book_instance.save()

			data = {
				'successMsg': 'Thanks for booking with Bryte!<br> You will receive a confirmation email with your booking information soon!<br><br>Team Bryte Photo',
			}

			# send the email
			# put location too
			msg_body = 'Dear ' + str(name) + ':\n\n' + 'Thanks for booking with Bryte Photo! Your headshot session is scheduled on ' + str(time) + ' at Brown University (115 George St, Wriston Quadrangle). \n\n We look forward to seeing you there!\n\nTeam Bryte Photo\nwww.brytephoto.com'
			admin_msg_body = str(name) + ' has booked a headshot!\n\nTime: ' + str(time) + '\n\n Bryte'
			try:
				# send both customer email and admin email
				send_mail('Your Booking with Bryte', msg_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
				send_mail('New Headshot Order', admin_msg_body, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
			except SMTPRecipientsRefused:
				print 'Email Not Sent!'
				pass

			return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


