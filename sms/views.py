from django.shortcuts import render
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from django_twilio.decorators import twilio_view
from twilio.twiml import Response

# Create your views here.
# -*- coding: utf-8 -*-

@twilio_view
def sms(request):
  name = request.POST.get('Body', '')
  msg = 'Hey %s, how are you today?' % (name)
  r = Response()
  r.message(msg)
  return r
