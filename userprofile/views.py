from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import get_template

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings
# Create your views here.
from .models import Profile
from .forms import ProfileEditForm
from reserve.models import Reservation

import json
from django.http import Http404, HttpResponse

import requests

@login_required
def profile(request):
	user = request.user
	profile = user.profile
	photographer = profile.photographer
	reservations = Reservation.objects.filter(photographer=photographer).order_by('-timestamp')
	all_reservations = Reservation.objects.all().order_by('-timestamp')
	context = {
		'name': user.username,
		'profile': profile,
		'reservations': reservations,
		'title_text': profile.user.username,
		'client_id': settings.CLIENT_ID,
		'all_reservations': all_reservations,
	}

	# get the oauth get request
	# wherever the redirect from stripe take place, 
	# grab the get request and make post request to stripe again
	if request.method == 'GET' and not photographer.stripe_user_id:
		auth_code = request.GET.get('code')
		secret = settings.STRIPE_SECRET_KEY
		url = 'https://connect.stripe.com/oauth/token'
		data = {
			'code': auth_code,
			'client_secret': secret,
			'grant_type': 'authorization_code'
		}
		if auth_code:
			r = requests.post(url, data)
			content = r.json()
			stripe_publishable_key = content.get('stripe_publishable_key')
			access_token = content.get('access_token')
			scope = content.get('scope')
			refresh_token = content.get('refresh_token')
			stripe_user_id = content.get('stripe_user_id')

			error = content.get('error')
			error_description = content.get('error_description')

			if stripe_user_id:
				photographer = profile.photographer
				photographer.scope = scope
				photographer.refresh_token = refresh_token
				photographer.stripe_user_id = stripe_user_id
				photographer.stripe_publishable_key = stripe_publishable_key
				photographer.access_token = access_token
				photographer.save()

				print 'Success!'
				print content


				context['auth_message'] = 'Your payment information has been successfully updated.'

			if error:
				context['auth_message'] = 'Authentication unsuccessful! error: ' + error + '. Description: ' + error_description + '.'

				print 'Error!'
				print error_description

	if request.method == 'POST':
		edit_form = ProfileEditForm(request.POST)
		if edit_form.is_valid():
			last_name = edit_form.cleaned_data.get('last_name')
			first_name = edit_form.cleaned_data.get('first_name')
			phone = edit_form.cleaned_data.get('phone')
			school = edit_form.cleaned_data.get('school')
			description = edit_form.cleaned_data.get('description')
			email = edit_form.cleaned_data.get('email')

			photographer = request.user.profile.photographer
			photographer.last_name = last_name
			photographer.first_name = first_name
			photographer.school = school
			photographer.email = email
			photographer.description = description
			photographer.phone = phone
			photographer.save()

		messages.add_message(request, messages.SUCCESS, 'Your profile was updated successfully')

	# get the message of editing profile
	storage = messages.get_messages(request)
	if storage:
		for message in storage:
			context['message'] = message

	return render(request, 'profile.html', context)


@login_required
def edit(request):
	context = {}

	# edit form for profile
	edit_form = ProfileEditForm()
	context['edit_form'] = edit_form
	context['title_text'] = 'Edit'

	return render(request, 'profile_edit.html', context)


def ajax_take(request):
	if request.is_ajax() and request.method == 'GET':
		res_id = request.GET.get('res_pk')
		print res_id
		reservation = get_object_or_404(Reservation, pk=res_id)
		photographer = reservation.photographer

		# update the taken attr
		reservation.is_taken = True
		reservation.save()

		# send emails
		html_content = get_template('email_is_taken_client.html')
		html_content_creative = get_template('email_is_taken_creative.html')
		d = {
			'business_name': reservation.business_name,
			'creative_full_name': photographer.get_full_name(),
			}
		c = {
			'business_name': reservation.business_name,
			'creative_full_name': photographer.get_full_name(),
			'email': reservation.email,
			'phone': reservation.phone,
			'client_full_name': reservation.first_name + ' ' + reservation.last_name,
			'date_range': reservation.date_range,
			'special_request': reservation.note,
		}

		html_content = str(html_content.render(d))
		html_content_creative = str(html_content_creative.render(c))

		to = reservation.email
		from_email = settings.SITE_EMAIL
		subject = 'Your project has been taken!'

		# send mail to client
		send_mail(subject, '', from_email,
    [to], fail_silently=False, html_message=html_content)


		to_creative = reservation.photographer.email
		subject_creative = 'Confirmation of the project'

		# send mail to creative
		send_mail(subject_creative, '', from_email,
			[to_creative], fail_silently=False, html_message=html_content_creative)


		# ajax
		data={}
		data['status'] = reservation.creative_status()

		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


def ajax_complete(request):
	if request.is_ajax() and request.method == 'GET':
		res_id = request.GET.get('res_pk')
		reservation = get_object_or_404(Reservation, pk=res_id)
		photographer = reservation.photographer

		# update the complete attr
		reservation.is_complete = True
		reservation.save()

		# send emails
		html_content = get_template('email_is_complete_client.html')

		pay_link = reverse('reserve_checkout')
		url = settings.SITE_URL + str(pay_link) + '?reservation=' + str(res_id)

		d = {
			'business_name': reservation.business_name,
			'creative_full_name': photographer.get_full_name(),
			'pay_url': url,
			}
		html_content = str(html_content.render(d))
		to = reservation.email
		from_email = settings.SITE_EMAIL
		subject = 'Your project is finished! Here\'s the next step'
		send_mail(subject, '', from_email,
    [to], fail_silently=False, html_message=html_content)


		data={}
		data['status'] = reservation.status()

		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404