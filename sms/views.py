from django.shortcuts import render
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from django_twilio.decorators import twilio_view
from twilio.twiml import Response

# Create your views here.
# -*- coding: utf-8 -*-

@twilio_view
def sms(request):
  r = Response()
  r.message('Hello from your Django app!')
  return r