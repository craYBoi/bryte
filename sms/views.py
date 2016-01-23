from django.shortcuts import render
# from django.http import HttpResponse
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
  client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

  client.messages.create(
    to="+13109139124", 
    body=msg, 
	) 

  # r = Response()
  # r.message(msg)
  return '<Response></Response>'
