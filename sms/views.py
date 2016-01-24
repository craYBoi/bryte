from django.shortcuts import render
from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from twilio.rest import TwilioRestClient 
from django_twilio.decorators import twilio_view
from twilio.twiml import Response
from django.conf import settings

from .models import Smser

# Create your views here.
# -*- coding: utf-8 -*-

@twilio_view
def sms(request):
	
	from_number = request.POST.get('From', '')
	content = request.POST.get('Body', '')

	if from_number == settings.BEN_CELL:
		if content:
			dest_num = content.split()[0]
			# add phone number validation here

			body = content[len(dest_num)+1:]
			if body:
				if len(dest_num) == 10:
					dest_num = '+1' + dest_num

				# send the sms
				send_msg(settings.TWILIO_CELL, dest_num, body)

				# send the confirmation back
				body = 'message sent to ' + dest_num
			else:
				body = 'There\'s no message body! Please try again'
		else:
			body = 'It\'s blank! please try again'

		r = Response()
		r.message(body)
		return r
	else:
		from_city = request.POST.get('FromCity', '')
		from_state = request.POST.get('FromState', '')
		msg = 'from: ' + from_number + ', ' + from_city + ', ' + from_state + '\n' + content
		send_msg(settings.TWILIO_CELL, settings.BEN_CELL, msg)

		# save the contact into database
		smser, created = Smser.objects.update_or_create(
    number=from_number, from_city=from_city, from_state=from_state)

	twiml = '<Response></Response>'
	return HttpResponse(twiml, content_type='text/xml')

	# r = Response()
	# r.message(msg)

# helper function to send text msg
def send_msg(input_from, input_to, input_body):
	client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

	client.messages.create(
		from_= input_from,
		to= input_to,
		body=input_body,
		)