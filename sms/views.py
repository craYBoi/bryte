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
  content = request.POST.get('Body', '')
  from_city = request.POST.get('FromCity', '')
  from_state = request.POST.get('FromState', '')
  msg = 'from: ' + from_city + ', ' + from_state + '\n' + content

  client.messages.create(
  	from_="+13137698688",
  	to="+13109139124",
  	body=msg,
  	)

  twiml = '<Response></Response>'
	 
	# client.messages.create( 
	# 	from="+13137698688",  
	# 	to="+13109139124",
	# 	body=msg, 
	# )


  # r = Response()
  # r.message(msg)
	# twiml = '<Response></Response>'
  return HttpResponse(twiml, content_type='text/xml')
