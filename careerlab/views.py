from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Timeslot, Booking, Signup

import json

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
				data = {'msg': 'There\'s an error signing up. Please try again.'}
				return HttpResponse(json.dumps(data), content_type='application/json')

		else:
			data = {'msg': 'This time slot is no longer available. Please select a different one.'}
			return HttpResponse(json.dumps(data), content_type='application/json')


		data = {
			'msg': 'Thanks for signing up ' + str(name) + '.<br><br>A confirmation email will be sent to you at \"' + str(email) + '\" with your booking information soon!<br><br>Team Bryte Photo',
		}

		# send the email confirmation
		msg_body = "Hi " + str(name) + ",\n\nYou\'ve book a headshot session at " + str(timeslot) + ". Congratulations for your free headshot! \n\nShow up to the CareerLAB 5 min. before your 15 min. timeslot is scheduled to begin. You'll have 3 minutes with your photographer, so make sure not to be late.\n\nIf you have any questions between now and your headshot session, shoot us an email at hello@brytephoto.com.\n\nYou can cancel the headshot session anytime by clicking the following link:\n" + b.generate_cancel_link() + "\n\nThanks, \nCareerLAB and Bryte Photo"
		try:
			send_mail('CareerLAB Headshot Signup Confirmation', msg_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
		except SMTPRecipientsRefused:
			print 'Email not sent'
			pass

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
			booking.cancel_order()
	return render(request, 'notification.html', context)