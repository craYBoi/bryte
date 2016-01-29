from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


import stripe
from newsletter.models import Price
from models import Purchase


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
	publishKey = settings.STRIPE_PUBLISHABLE_KEY
	customer_id = request.user.profile.stripe_id
	is_success = False
	is_decline = False

	if request.method == 'POST':
		price_id = request.POST.get('hidden')
		price = Price.objects.get(pk=price_id)
		token = request.POST['stripeToken']
		
		# Create the charge on Stripe's servers - this will charge the user's card
		try:
			customer = stripe.Customer.create(
				source=token,
			)
			charge = stripe.Charge.create(
				amount=price.stripe_price, # amount in cents, again
				currency="usd",
				customer=customer.id,
				description=price.title
			)
			is_success = True
		except Exception as e:
				# The card has been declined
			is_decline = True
			pass
		

# store the purchase into the database
	if request.method == 'POST':
		price_id = request.POST.get('hidden')
		price = Price.objects.get(pk=price_id)
		profile = request.user.profile
		Purchase.objects.create(package=price, user=profile)

	prices = Price.objects.all()
	context = {
		'prices': prices,
		'publishKey': publishKey,
		'title_text': 'Checkout',
	}
	template='pay.html'
	if is_success:
		return redirect('/success')
	if is_decline:
		return redirect('/')
	return render(request, template, context)


def checkout_finish(request):
	if request.method == 'POST':
		email = request.POST.get('stripeEmail')
		token = request.POST.get('stripeToken')
		print token

	context = {
		'title_text': 'Successful!',
	}
	return render(request, 'checkout_finish.html', context)
