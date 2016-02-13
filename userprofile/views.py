from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
from .models import Profile
from .forms import ProfileEditForm
from reserve.models import Reservation


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
	}

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