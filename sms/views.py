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
  msg = 'from: ' + from_city + ', ' + from_state + '\n' + 'content:\n' + content

  # send the msg to me and Michael
	ACCOUNT_SID = "ACa508a195425ca7341d5469a54a91cb36" 
	AUTH_TOKEN = "4005b7c244086f9986d6375b2b7530e3" 
	 
	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
	 
	client.messages.create( 
		from="+13137698688",  
		to="+13109139124",
		body=msg, 
	)


  # r = Response()
  # r.message(msg)
	twiml = '<Response></Response>'
  return return HttpResponse(twiml, content_type='text/xml')
