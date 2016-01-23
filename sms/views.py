from django.shortcuts import render
from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from twilio.rest import TwilioRestClient 
from django_twilio.decorators import twilio_view
from twilio.twiml import Response
from django.conf import settings

# Create your views here.
# -*- coding: utf-8 -*-

@twilio_view
def sms(request):
	
	from_number = request.POST.get('From', '')
	content = request.POST.get('Body', '')

	# if from_number == settings.BEN_CELL:
	if str(from_number) == '+13109139124'
		if content:
			dest_num = content.split()[0]
			body = content[len(dest_num)+1:]
			if len(dest_num) == 10:
				dest_num = '+1' + dest_num

			# send the sms
			# send_msg(settings.TWILIO_CELL, dest_num, body)
			send_msg('+13137698688', dest_num, body)
		else:
			body = 'invalid format, please send again'
			r = Response()
			r.message(body)
			return r
	else:
		from_city = request.POST.get('FromCity', '')
		from_state = request.POST.get('FromState', '')
		msg = 'from: ' + from_number + ', ' + from_city + ', ' + from_state + '\n' + content
		# send_msg(settings.TWILIO_CELL, settings.BEN_CELL, msg)
		send_msg('+13137698688', '+13109139124', msg)

	twiml = '<Response></Response>'
	return HttpResponse(twiml, content_type='text/xml')

	# r = Response()
	# r.message(msg)

# helper function to send text msg
def send_msg(input_from, input_to, input_body):
	# client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
	client = TwilioRestClient("ACa508a195425ca7341d5469a54a91cb36", "4005b7c244086f9986d6375b2b7530e3")

	client.messages.create(
		from_= input_from,
		to= input_to,
		body=input_body,
		)