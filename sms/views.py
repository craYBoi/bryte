from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def sms(request):
	twiml = '<Response><Sms>Hello from your Django app!</Sms></Response>'
	return HttpResponse(twiml, content_type='text/xml')