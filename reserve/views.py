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
	fav_photographers = None
	reserve_form = ReserveForm()
	context = {}

	if request.method == "GET":
		form_photographer_name = 'fav_photographer'
		form_package_name = 'fav_package'

		photographer_list = request.GET.getlist(form_photographer_name)

		fav_photographers = [get_object_or_404(Photographer, pk=id) for id in photographer_list]
		package_id = request.GET.get(form_package_name)
		if package_id:
			fav_package = get_object_or_404(Price, pk=package_id)


		context['title_text'] = 'Reserve'
		context['fav_photographers'] = fav_photographers
		context['fav_package'] = fav_package
		context['reserve_form'] = reserve_form
		

	if request.method == 'POST':
		reserve_form = ReserveForm(request.POST)
		if reserve_form.is_valid():

			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
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
				return redirect(reverse('packages'))
			fav_package = get_object_or_404(Price, pk=package_id)

			# store reservations and send email
			photographer_names = ''
			for fav_photographer in fav_photographers:
				res = Reservation.objects.create(
					photographer=fav_photographer,
					business_name=business_name,
					note=special_request,
					phone=phone,
					email=email,
					price=fav_package,
					date_range=date_range,
					first_name=first_name,
					last_name=last_name,
					)
				photographer_names += fav_photographer.get_full_name() + ' '

			# send email
			msg_body = 'Business: ' + str(business_name) + '\nFull name: ' + first_name + ' ' + last_name + '\nPackage: ' + fav_package.title + ' ' + fav_package.shared_title + '\nCreative: ' + photographer_names + '\nDate: ' + str(date_range) + '\nPhone: ' + str(phone) + '\nEmail: ' + str(email) + '\nSpecial Requests: ' + str(special_request)
			send_mail('New Reservation: ' + business_name, 'You got a new reservation\n\n' + msg_body, 'hello@brytephoto.com',
			['yb@brown.edu'], fail_silently=False)

			client_msg_body = 'Dear ' + last_name + ':\n\n' + 'We are processing your booking. We will match you with a creative and let you know as soon as we have!\n\nHere\'s the detail of your booking:\n'
			send_mail('Your Booking with Bryte', client_msg_body + msg_body + '\n\nThanks,\nBryte Photo Inc\nhello@brytephoto.com', 'hello@brytephoto.com',
			[email], fail_silently=False)

			return redirect(reverse('reserve_success_new'))	
		else:
			messages.add_message(request, messages.ERROR, 'The form you entered is not valid, please try again')
			photographer_list = request.POST.getlist('fav_photographers')
			package_id = request.POST.get('fav_package')
			url = '?'+ 'fav_photographer' + '=' + str(photographer_list[0]) + '&' +  'fav_package' +'=' + str(package_id)
			return redirect('/reserve/' + url)

	return render(request, 'reserve.html', context)


def reserve_success(request):
	context = {
		'title_text': 'Successfully Reserved!',
	}

	return render(request, 'reserve_success.html', context)



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

	if request.method == 'GET':
		rid = request.GET.get('reservation')
		reservation = get_object_or_404(Reservation, pk=rid)

		# check the status of the reservation,
		# only allow to pay if the reservation is_complete

		context['res'] = reservation
		context['price'] = reservation.price



	# if request.method == 'POST':
	# 	# create a form to process the data
	# 	pid = request.POST.get('photographer')
	# 	photographer = Photographer.objects.get(pk=pid)
	# 	reserve_form = ReserveDetailStudentForm(request.POST)

	# 	if reserve_form.is_valid():
	# 		# store the reservation to database, with purchased being false
	# 		photographer = reserve_form.cleaned_data.get('photographer')
	# 		datetime = reserve_form.cleaned_data.get('datetime')
	# 		price = reserve_form.cleaned_data.get('package')
	# 		note = reserve_form.cleaned_data.get('note')
	# 		phone = reserve_form.cleaned_data.get('phone')

	# 		# validate the time

	# 		# other intelligent validations

	# 		context['photographer'] = photographer
	# 		context['datetime'] = datetime
	# 		context['price'] = price
	# 		context['note'] = note
	# 		context['phone'] = phone

	# 		# store the reservation
	# 		res = Reservation.objects.create(photographer=photographer,
	# 		datetime=datetime, note=note, phone=phone, price=price, complete=False)

	# 		# pass the reservation too as hidden field for successpage to catch it
	# 		context['res'] = res.pk

		# else:
		# 	slug = photographer.slug

			# add the message
			# messages.add_message(request, messages.ERROR, 'The form is not valid. Please try again')
			# return redirect(reverse('reserve_detail', kwargs={'slug': slug}))

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
		reservation = get_object_or_404(Reservation, pk=res_id)
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

			# need to work on the redirection after failing
			return redirect(reverse('home'))
		else:
			# toggle is_paid
			reservation.is_paid = True
			reservation.save()

			# send the email
			try:
				send_mail('Successfully Paid!',
					'Thank you for the payment!',
					settings.EMAIL_HOST_USER,
					[reservation.email],
					fail_silently=False
				)

				send_mail('Awesome Work!',
					'The client has paid $' + str(reservation.price.price) + ' for your project! You will receive $' +  str(reservation.price.price*0.8) + '\nAwesome Job!',
					settings.EMAIL_HOST_USER,
					[photographer.email],
					fail_silently = False,
				)
			except SMTPRecipientsRefused:
				print 'Email not set!'
				pass

			# add to context to display
			context['photographer'] = reservation.photographer
			context['phone'] = reservation.phone
	else:
		# for security
		return redirect('/photographer')

	return render(request, 'reserve_success.html', context)








