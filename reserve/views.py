from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ReserveForm, ReserveDetailStudentForm, ReserveDetailProForm

# Create your views here.
from photographer.models import Photographer
from newsletter.models import Price
from .models import Reservation

import stripe


def reserve(request):

	reserve_form = ReserveForm(request.POST or None)
	if reserve_form.is_valid():
		reserve_form.save()
		reserve_form.send_email()
		return redirect('reserve_success')

	context = {
		'reserve_form': reserve_form,
		'title_text': 'Reserve',
	}
	return render(request, 'reserve.html', context)


@login_required
def reserve_detail(request, slug):

	photographer = Photographer.objects.get(slug=slug)
	is_student = photographer.is_student

	if is_student:
		reserve_form = ReserveDetailStudentForm(initial={'photographer': photographer})
	else:
		reserve_form = ReserveDetailProForm(initial={'photographer': photographer})


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


@login_required
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
		if photographer.is_student:
			reserve_form = ReserveDetailStudentForm(request.POST)
		else:
			reserve_form = ReserveDetailProForm(request.POST)

		if reserve_form.is_valid():
			# store the reservation to database, with purchased being false
			photographer = reserve_form.cleaned_data.get('photographer')
			datetime = reserve_form.cleaned_data.get('datetime')
			price = reserve_form.cleaned_data.get('package')
			note = reserve_form.cleaned_data.get('note')
			phone = reserve_form.cleaned_data.get('phone')

			context['photographer'] = photographer
			context['datetime'] = datetime
			context['price'] = price
			context['note'] = note
			context['phone'] = phone

			# store the reservation
			res = Reservation.objects.create(photographer=photographer, profile=request.user.profile,
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


@login_required
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

		if token:
			stripe.api_key = settings.STRIPE_SECRET_KEY
		
		# Create the charge on Stripe's servers - this will charge the user's card
		try:
			# customer = stripe.Customer.create(
			# 	source=token,
			# )
			customer_id = request.user.profile.stripe_id
			charge = stripe.Charge.create(
				amount=price.stripe_price, # amount in cents, again
				currency="usd",
				customer=customer_id,
				description=price.title
			)
			is_success = True
		except Exception as e:
			# The card has been declined
			messages.add_message(request, messages.ERROR, 'The payment is unsuccessful')
			res_id = request.POST.get('reservation')
			reservation = Reservation.objects.get(pk=res_id)
			photographer = reservation.photographer
			return redirect(reverse('reserve_detail', kwargs={'slug': photographer.slug}))


		if is_success:
			# change reservation complete from False to True
			res_id = request.POST.get('reservation')
			reservation = Reservation.objects.get(pk=res_id)
			reservation.complete = True
			reservation.save()

			# add to context to display
			context['photographer'] = reservation.photographer
			context['phone'] = reservation.phone
	else:
		# for security
		return redirect('/photographer')

	return render(request, 'reserve_success.html', context)








