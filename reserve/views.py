from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .forms import ReserveForm, ReserveDetailStudentForm

# Create your views here.
from photographer.models import Photographer
from newsletter.models import Price
from .models import Reservation

import stripe
import datetime
from mixpanel import Mixpanel

stripe.api_key = settings.STRIPE_SECRET_KEY
# mp = Mixpanel(settings.MIXPANEL_TOKEN)

def reserve(request):

	fav_package=''
	if request.method == "POST":
		photographer_list = request.POST.getlist('fav_photographer')
		fav_photographers = [get_object_or_404(Photographer, pk=id) for id in photographer_list]
		package_id = request.POST.get('fav_package')
		if package_id:
			fav_package = get_object_or_404(Price, pk=package_id)

	reserve_form = ReserveForm()

	context = {
		'reserve_form': reserve_form,
		'title_text': 'Reserve',
		'fav_photographers': fav_photographers,
		'fav_package': fav_package,
	}
	return render(request, 'reserve.html', context)


def reserve_success(request):
	context = {
		'title_text': 'Successfully Reserved!',
	}
	if request.method == "POST":
		date_range = request.POST.get('date_range')
		business_name = request.POST.get('business_name')
		special_request = request.POST.get('special_request')
		phone = request.POST.get('phone')
		email = request.POST.get('email')
		photographer_list = request.POST.getlist('fav_photographers')
		fav_photographers = [get_object_or_404(Photographer, pk=id) for id in photographer_list]
		package_id = request.POST.get('fav_package')
		if not package_id:
			messages.add_message(request, messages.ERROR, 'You haven\'t select packages yet. Please try again')
			return redirect(reverse('get_started'))
		fav_package = get_object_or_404(Price, pk=package_id)

		# store reservations and send email
		photographer_names = ''
		for fav_photographer in fav_photographers:
			res = Reservation.objects.create(
				photographer=fav_photographer,
				business_name=business_name,
				note=special_request,
				phone=phone,
				price=fav_package,
				date_range=date_range,
				)
			photographer_names += fav_photographer.get_full_name() + ' '

		# send email
		msg_body = 'You got a new reservation!!\n\nBusiness: ' + str(business_name) + '\nPackage: ' + fav_package.title + '\nPhotographers: ' + photographer_names + '\nDate: ' + str(date_range) + '\nPhone: ' + str(phone) + '\nEmail: ' + str(email) + '\nSpecial Request: ' + str(special_request)
		send_mail('New Reservation!!', msg_body, 'hello@brytephoto.com',
    ['hello@brytephoto.com', 'yb@brown.edu'], fail_silently=False)

		return render(request, 'reserve_success.html', context)

	messages.add_message(request, messages.ERROR, 'There\'s something wrong. Please try again')
	return redirect(reverse('get_started'))


def reserve_detail(request, slug):

	photographer = Photographer.objects.get(slug=slug)
	reserve_form = ReserveDetailStudentForm(initial={'photographer': photographer})

	# track user click reserve

	context = {
		'title_text': 'Reserve ' + photographer.get_full_name(),
		'photographer': photographer,
		'reserve_form': reserve_form,
	}

	# display the message by putting it to context
	storage = messages.get_messages(request)
	if storage:
		for message in storage:
			context['message'] = message


	return render(request, 'reserve_detail.html', context)


def checkout(request):

	context = {
		'title_text': 'Checkout',
	}

	publishKey = settings.STRIPE_PUBLISHABLE_KEY
	context['publish_key'] = publishKey	

	if request.method == 'POST':
		# create a form to process the data
		pid = request.POST.get('photographer')
		photographer = Photographer.objects.get(pk=pid)
		reserve_form = ReserveDetailStudentForm(request.POST)

		if reserve_form.is_valid():
			# store the reservation to database, with purchased being false
			photographer = reserve_form.cleaned_data.get('photographer')
			datetime = reserve_form.cleaned_data.get('datetime')
			price = reserve_form.cleaned_data.get('package')
			note = reserve_form.cleaned_data.get('note')
			phone = reserve_form.cleaned_data.get('phone')

			# validate the time

			# other intelligent validations

			context['photographer'] = photographer
			context['datetime'] = datetime
			context['price'] = price
			context['note'] = note
			context['phone'] = phone

			# store the reservation
			res = Reservation.objects.create(photographer=photographer,
			datetime=datetime, note=note, phone=phone, price=price, complete=False)

			# pass the reservation too as hidden field for successpage to catch it
			context['res'] = res.pk

		else:
			slug = photographer.slug

			# add the message
			messages.add_message(request, messages.ERROR, 'The form is not valid. Please try again')
			return redirect(reverse('reserve_detail', kwargs={'slug': slug}))

	else:
	# for security
		return redirect('/photographer')

	return render(request, 'checkout.html', context)



def success(request):
	is_success = False

	context = {
		'title_text': 'Success!',
	}

	if request.method == 'POST':
		# to check whether it's the stripe form or reserve form
		price_id = request.POST.get('hidden')
		price = Price.objects.get(pk=price_id)
		token = request.POST.get('stripeToken')

		# get the photographer stripe id
		res_id = request.POST.get('reservation')
		reservation = Reservation.objects.get(pk=res_id)
		photographer = reservation.photographer

		# track somebody paid
		# res_id = request.POST.get('reservation')
		# reservation = Reservation.objects.get(pk=res_id)
		# photographer = reservation.photographer
		# mp.track(request.user.id, 'Process Payment', {
		# 		'customer': str(request.user.username),
		# 		'photographer': photographer.get_full_name(),
		# 		'reservation': 'Reservation ID: ' + str(res_id),
		# 	})
		
		# Create the charge on Stripe's servers - this will charge the user's card
		try:
			commission = float(settings.COMMISSION)
			fee = int(commission * price.stripe_price)

			charge = stripe.Charge.create(
				amount=price.stripe_price, # amount in cents, again
				currency="usd",
				source=token,
				destination= photographer.stripe_user_id,
				application_fee=fee,
			)
			is_success = True
		except stripe.error.CardError, e:
			body = e.json_body
			err = body['error']
			error_status = 'Status: ' + str(e.http_status) + '\n'
			error_type = 'Type: ' + err.get('type') + '\n'
			error_msg = 'Message: ' + err.get('message')
			# The card has been declined
			error_str = ''
			if error_status:
				error_str += error_status
			if error_type:
				error_str += error_type
			if error_msg:
				error_str += error_msg
			messages.add_message(request, messages.ERROR, error_str)
			return redirect(reverse('reserve_detail', kwargs={'slug': photographer.slug}))


		if is_success:
			# change reservation complete from False to True
			res_id = request.POST.get('reservation')
			reservation = Reservation.objects.get(pk=res_id)
			reservation.complete = True
			reservation.save()

			# send the email
			send_mail('Successfully Reserved!',
				'Thank you for the reservation! You have reserved ' + reservation.photographer.get_full_name() + '! -- Team Bryte',
				settings.EMAIL_HOST_USER,
				['chailatte.byy@gmail.com'],
				fail_silently=False
				)

			# add to context to display
			context['photographer'] = reservation.photographer
			context['phone'] = reservation.phone
	else:
		# for security
		return redirect('/photographer')

	return render(request, 'reserve_success.html', context)








