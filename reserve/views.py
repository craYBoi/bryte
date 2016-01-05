from django.shortcuts import render, redirect
from django.core.mail import send_mail

from .forms import ReserveForm

# Create your views here.


def reserve(request):
	reserve_form = ReserveForm(request.POST or None)
	if reserve_form.is_valid():
		reserve_form.save()
		send_mail('Successfully Registered!', 
			'Your Email message.', 
			'bestprofpics@gmail.com', 
			['byyagp@gmail.com'], 
			fail_silently=False)
		return redirect('reserve_success')

	context = {
		'reserve_form': reserve_form,
		'title_text': 'Reserve',
	}
	return render(request, 'reserve.html', context)


def success(request):
	context = {
		'title_text': 'Success!',
	}
	return render(request, 'reserve_success.html', context)