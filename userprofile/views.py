from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
# Create your views here.
from .models import Profile
from .forms import ProfileEditForm
from reserve.models import Reservation

import requests

@login_required
def profile(request):
	user = request.user
	profile = user.profile
	reservations = Reservation.objects.filter(profile=profile).order_by('timestamp')
	context = {
		'name': user.username,
		'profile': profile,
		'reservations': reservations,
		'title_text': profile.user.username,
		'client_id': settings.CLIENT_ID,
	}

	# get the oauth get request
	# wherever the redirect from stripe take place, 
	# grab the get request and make post request to stripe again
	if request.method == 'GET':
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
			photographer = profile.photographer
			photographer.scope = scope
			photographer.refresh_token = refresh_token
			photographer.stripe_user_id = stripe_user_id
			photographer.stripe_publishable_key = stripe_publishable_key
			photographer.access_token = access_token
			photographer.save()

			context['auth_message'] = 'You have been authenticated! Enjoy Bryte!'

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