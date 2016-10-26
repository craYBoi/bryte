from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import serializers
from django.core.urlresolvers import reverse

from .models import Timeslot, Booking, Signup, Nextshoot, OriginalHeadshot, HeadshotPurchase, HeadshotOrder

from random import SystemRandom
import string
import json
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY

# School url definition
# brown -> Brown University
# ric -> Rhode Island College
# bu -> Boston University
# bc -> Boston College
# ccri -> Community College of Rhode Island


def index(request, school='brown'):

	context = {
		'brown_careerlab': 1,
	}
	timeslots = ''
	nextshoot = ''
	title = ''
	bg_url = ''
	logo_url = ''
	school_name = ''
	school_abbr = ''
	school_url = ''
	school_bryte_url = ''
	school_title = ''
	school_location = ''
	main_color = 'red'
	main_bg_color = 'red_bg'
	secondary_bg_color = 'background_pink'

	modal_form_title = ''

	# view logic for different schools here
	# filter by the school name and pick the first
	if school.lower() == 'brown':
		title = 'Bryte & CareerLab Brown University Headshot'
		nextshoot = Nextshoot.objects.filter(school='Brown University').order_by('-date')
		bg_url = static('img/brown_campus.jpg')
		logo_url = static('logo/brown_logo.png')
		school_name = 'Brown University CareerLAB'
		school_url = 'http://www.brown.edu'
		school_bryte_url = 'brown'
		school_abbr = 'Brown'
		school_title = 'CareerLAB'
		school_location = 'CareerLAB'
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404


	if school.lower() == 'gradcon':
		title = 'Bryte & GradCON'
		nextshoot = Nextshoot.objects.filter(school='Brown GradCON').order_by('-date')
		bg_url = static('img/brown_campus.jpg')
		logo_url = static('logo/gradcon.jpg')
		school_name = 'Brown University CareerLAB'
		school_url = 'https://www.brown.edu/campus-life/support/careerlab/GradCon'
		school_bryte_url = 'gradcon'
		school_abbr = 'Brown GradCON'
		school_title = 'Brown University GradCON'
		school_location = 'CareerLAB'
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404


	if school.lower() == 'ric':
		title = 'Bryte & Rhode Island College'
		nextshoot = Nextshoot.objects.filter(school='Rhode Island College').order_by('-date')
		bg_url = static('img/brown_campus.jpg')
		logo_url = static('img/ric/logo.gif')
		school_name = 'Rhode Island College'
		school_url = 'http://www.ric.edu'
		school_bryte_url = 'ric'
		school_abbr = 'RIC'
		school_title = 'Career Planning'
		school_location = '2nd Floor Alger Hall Student Lounge'
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404


	elif school.lower() == 'bu' or school.lower() == 'bostonuniversity':
		title = 'Bryte & Boston University Headshot'
		nextshoot = Nextshoot.objects.filter(school='Boston University').order_by('-date')
		bg_url = static('img/bu/bg.jpg')
		logo_url = static('img/bu/logo.png')
		school_name = 'Boston University Feld Career Center'
		school_url = 'http://www.bu.edu'
		school_title = 'BU Career Center'
		school_bryte_url = 'bu'
		school_abbr = 'BU'
		school_location = 'GSU 2nd floor'

		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404


	elif school.lower() == 'ccriknight':
		title = 'Bryte & the Community College of Rhode Island Knight Campus Headshot'
		bg_url = static('img/ccri/bg.JPG')
		logo_url = static('img/ccri/logo.png')
		school_name = 'Community College of Rhode Island'
		school_url = 'http://www.ccri.edu'
		school_bryte_url = 'ccriknight'
		school_abbr = 'CCRI'
		school_title = 'Career Planning'
		school_location = 'the Great Hall'
		main_color = 'green'
		main_bg_color = 'green_bg'
		secondary_bg_color = 'light_green_bg'
		nextshoot = Nextshoot.objects.filter(school='Community College of Rhode Island').order_by('-date')
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404



	elif school.lower() == 'ccriflanagan':
		title = 'Bryte & the Community College of Rhode Island Flanagan Campus Headshot'
		bg_url = static('img/ccri/bg.JPG')
		logo_url = static('img/ccri/logo.png')
		school_name = 'Community College of Rhode Island'
		school_url = 'http://www.ccri.edu'
		school_bryte_url = 'ccriflanagan'
		school_abbr = 'CCRI'
		school_title = 'CCRI Flanagan Campus'
		school_location = 'CCRI Flanagan Campus, rear of the cafeteria'
		main_color = 'green'
		main_bg_color = 'green_bg'
		secondary_bg_color = 'light_green_bg'
		nextshoot = Nextshoot.objects.filter(school='Community College of Rhode Island Flanagan').order_by('-date')
		if nextshoot:
			nextshoot = nextshoot[0]
			timeslots = nextshoot.timeslot_set.filter(is_available=True).order_by('time')	
		else:
			raise Http404




	context['title_text'] = title
	context['timeslots'] = timeslots
	context['next_shoot'] = nextshoot
	context['logo_url'] = logo_url
	context['bg_url'] = bg_url
	context['school_url'] = school_url
	context['school_name'] = school_name
	context['school_title'] = school_title
	context['school_bryte_url'] = school_bryte_url
	context['school_location'] = school_location
	context['school_abbr'] = school_abbr

	context['main_color'] = main_color
	context['main_bg_color'] = main_bg_color
	context['secondary_bg_color'] = secondary_bg_color

	# next_shoot = Nextshoot.objects.first()
	# timeslots = next_shoot.timeslot_set.filter(is_available=True, active=True).order_by('time')
	# timeslots = Timeslot.objects.filter(active=True, is_available=True).order_by('time')
	# if timeslots:
	# 	next_shoot = timeslots.first().shoot

	return render(request, 'careerlab_index.html', context)


def book(request):
	if request.is_ajax() and request.method == 'POST':

		data = {}

		email = request.POST.get('email')
		name = request.POST.get('name')
		time_id = request.POST.get('time')
		timeslot = get_object_or_404(Timeslot, pk=time_id)
		shoot = timeslot.shoot
		emails = [e.email for elem in shoot.timeslot_set.all() for e in elem.booking_set.all()]

		# avoid duplicate booking
		if email in emails:
			data['msg'] = 'Looks like you have already booked a headshot. If you have not recieved a confirmation email, you will get one soon. We have you in the system :)<br>'		
		else:

			# increment the timeslot first to reduce confliction
			if timeslot.is_available:
				try:
					b = Booking.objects.create(
						email = email,
						name = name,
						timeslot = timeslot,
						)
				except Exception, e:
					raise e
					data['msg'] = 'There\'s an error signing up. Please try again.'
				else:
					# delete record in the signup list
					if email in [signup.email for signup in Signup.objects.all()]:
						try:
							signup = get_object_or_404(Signup, email=email)
						except Exception, e:
							print e
							pass
						else:
							signup.delete()

					# send email
					b.booking_confirmation_email()

					first_name = name.split(' ')[0]
					data['msg'] = 'Thanks for signing up ' + first_name + '.<br><br>A confirmation email will be sent to you at \"' + str(email) + '\" with your booking information soon!<br><br>Team Bryte'

			else:
				data['msg'] = 'This time slot is no longer available. Please select a different one.'


		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		# for mobile
		data = {}
		data['msg'] = 'There seems to be a little problem signing up, did you use your school email?'
		return HttpResponse(json.dumps(data), content_type='application/json')


def signup(request):
	if request.is_ajax() and request.method == 'POST':

		email = request.POST.get('email')
		name = request.POST.get('name')
		shoot_pk = request.POST.get('shoot')

		print shoot_pk

		data = {}

		# avoid duplicate signup
		if email in [signup.email for signup in Signup.objects.all()]:
			data['msg'] = 'It seems that you have already signed up!<br>We will notify at ' + str(email) + ' whenever next headshot session is available!<br><br>Thanks!<br>Team Bryte'
		else:
			# get the first shooting instance
			shoot = get_object_or_404(Nextshoot, pk=shoot_pk)
			try:
				s = Signup.objects.create(
					email = email,
					name = name,
					shoot = shoot,
					)
			except Exception, e:
				print e
				data['msg'] = 'There\'s an error signing up. Please try again.'
				pass
			else:
				first_name = name.split(' ')[0]
				data['msg'] = 'Thanks for signing up ' + str(first_name) + '. We will notify you for the next headshot session!<br><br>Team Bryte'

		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		# for mobile
		data = {}
		data['msg'] = 'There seems to be a little problem signing up, did you use your school email?'
		return HttpResponse(json.dumps(data), content_type='application/json')

# could subject to change to Shoot school name
def cancel_order(request):
	context = {
		'brown_careerlab': 1,
		'title_text': 'Cancel your signup',
		'notification_text': 'You have successfully cancelled your headshot!',
	}
	if request.method == 'GET':
		order_id = request.GET.get('order_id')
		try:
			booking = get_object_or_404(Booking, hash_id=order_id)
		except Exception, e:
			pass
		else:
			name = booking.name
			email = booking.email
			timeslot = booking.timeslot
			shoot = timeslot.shoot
			first_name = name.split(' ')[0]

			# need to disable cancellation after the shoot is closed
			if not shoot.active:
				context['notification_text'] = 'You cannot cancel the booking right now since the shoot is already closed'
				return render(request, 'notification.html', context)

			# generate the correct booking url in email
			url = ''
			if shoot.school == 'Community College of Rhode Island':
				url = 'www.brytephoto.com/school/ccriknight'
			elif shoot.school == 'Community College of Rhode Island Flanagan':
				url = 'www.brytephoto.com/school/ccriflanagan'
			elif shoot.school == 'Brown University':
				url = 'www.brytephoto.com/school/brown'
			elif shoot.school == 'Boston University':
				url = 'www.brytephoto.com/school/bu'
			elif shoot.school == 'Rhode Island College':
				url = 'www.brytephoto.com/school/ric'
			else:
				url = ''

			booking.cancel_order()
			msg_body = 'Hi ' + str(first_name) + ',\n\nThis email is to confirm you have cancelled your Bryte Photo headshot on ' + str(booking.timeslot) + '. If you would like to book a different time slot you can sign up here:\n\n'+ url +'\n\nBest,\nTeam Bryte'
			try:
				send_mail('Cancellation confirmation - Bryte Photo',
					msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [email],
					fail_silently=False)
			except Exception, e:
				print 'Email not sent'
				pass

	return render(request, 'notification.html', context)


def tips(request):
	context = {
		'brown_careerlab': 1,
		'title_text': 'Bryte Photo Headshot Tips',
	}
	return render(request, 'careerlab_tips.html', context)



def pay(request):
	context = {
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
		'title_text': 'Checkout at Bryte Photo',
	}
	if request.method == 'POST':
		token = request.POST.get('stripeToken')
				# charge
		try:
			charge = stripe.Charge.create(
				amount = 1199,
				currency="usd",
				source=token,
				description="Bryte Passport Photo"
			)
		except stripe.error.CardError, e:
			print e
			data = {'successMsg': 'There\'s an error charging your card. Please provide another card',}
			return HttpResponse(json.dumps(data), content_type='application/json')
		else:
			context['notify'] = 'Thanks! You have successfully paid! Thanks for using Bryte!'

	return render(request, 'careerlab_pay.html', context)


def headshot_index(request):
	# request.session.flush()
	if request.method == 'GET':

		if request.session.has_key('booking'):
			booking_id = request.session.get('booking')
		else:
			booking_id = request.GET.get('id')


		# if people try to access headshot url directly
		# need to change. filter() and orderby timestamps and take the first for now [DONE]
		bookings = Booking.objects.filter(hash_id=booking_id).order_by('-timestamp')
		if bookings:
			booking = bookings[0]
		else:
			return redirect('headshot_error')


		shoot = booking.timeslot.shoot
		if not shoot.is_serving:
			return redirect('headshot_expire')

		# try:
		# 	booking = get_object_or_404(Booking, hash_id=booking_id)
		# except Exception, e:
		# 	return redirect('headshot_error')


		# set session expiry 1.5 hours
		request.session.set_expiry(5000)

		# create a session
		request.session['booking'] = booking_id


		# if not request.session.has_key('order_total'):
		# 	request.session['order_total'] = 0


		headshots = booking.originalheadshot_set.all()
		headshot_urls = [a.raw_url for a in headshots]
		headshot_ids = [a.hash_id for a in headshots]


		# detect second round if prev stage is review
		# if request.session.get('stage') == 'review':
		# 	request.session['proceed'] = True

		# if proceed flag is on, meaning this is at least the second round, also add extra price for additional photo

		# show my cart
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)

		order_total = sum(a.total for a in orders)

		context = {
			'title_text': 'Select Photos',
			'myheadshot': 1,
			'headshots': zip(headshot_urls, headshot_ids),
			'proceed': request.session.get('proceed'),
			'orders': orders,
			'order_total': order_total,
		}


		# add the purchase instance to session and update the total
		# if request.session.get('proceed') and request.session.get('stage') == 'review':

		# 	# show cart if second or more rounds
		# 	request.session['cart'] = True


		# 	# store order instance in session
		# 	hs_id = request.session['hs_id']
		# 	touchup = request.session['touchup']
		# 	background = request.session['background']
		# 	package = request.session['package']
		# 	special_request = request.session.get('special_request')


		# 	total = request.session.get('total')

		# 	hs = get_object_or_404(OriginalHeadshot, hash_id=hs_id)

		# 	# create an purchase instance to store the order
		# 	hp = HeadshotPurchase(
		# 		image=hs,
		# 		touchup = touchup,
		# 		background = background,
		# 		package = package,
		# 		total = total,
		# 		special_request = special_request,
		# 		)

		# 	# already got a few rounds
		# 	orders = []
		# 	if request.session.has_key('order'):

		# 		for order in serializers.deserialize('json', request.session.get('order')):
		# 			orders.append(order.object)
		# 		orders.append(hp)
		# 	# second round
		# 	else:
		# 		orders = [hp]

		# 	# to show the cart
		# 	context['orders'] = orders

		# 	# update the order total
		# 	request.session['order_total'] += request.session['total']
			

		# 	# reset the subtotal to 0
		# 	request.session['total'] = 0

		# 	# reset special request
		# 	if request.session.get('special_request'):
		# 		del request.session['special_request']

		# 	# print orders
		# 	request.session['order'] = serializers.serialize('json', orders)


		# context['show_button'] = request.session.get('order')

		# if session expires, check if booking has ordered before, if so no free

		# request.session['proceed'] = HeadshotOrder.objects.filter(booking=booking).exists()

		# context['order_total'] = request.session['order_total']
		# context['cart'] = request.session.get('cart')
		# set the stage
		# request.session['stage'] = 'index'

		return render(request, 'order_index.html', context)
	else:
		return redirect('headshot_error')



def headshot_style(request):

	if request.session.has_key('booking') and request.method == 'GET':
		hs_id = request.GET.get('hs_pk')
		hs = get_object_or_404(OriginalHeadshot, hash_id=hs_id)

		request.session['hs_id'] = hs_id

		booking = hs.booking

		# get shoot and it's package prices
		shoot = booking.timeslot.shoot

		# get the original photos
		headshots = booking.originalheadshot_set.all()
		headshot_urls = [a.raw_url for a in headshots]
		headshot_ids = [a.hash_id for a in headshots]


		# show my cart
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)

		order_total = sum(a.total for a in orders)


		if request.session.has_key('proceed'):
			request.session['proceed'] = request.session['proceed'] or HeadshotOrder.objects.filter(booking=booking).exists()
		else:
			request.session['proceed'] = HeadshotOrder.objects.filter(booking=booking).exists()

		print 'proceed in style:',
		print request.session['proceed']

		context = {
			'myheadshot': 1,
			'title_text': 'Style Your Photo',
			'orders': orders[::-1],
			'order_total': order_total,
			'hs_id': hs_id,
			'hs': hs,
			'cart': request.session.get('cart'),
			'proceed': request.session.get('proceed'),
			'headshots': zip(headshot_urls, headshot_ids),
			'shoot': shoot,
		}

		# set stage
		# request.session['stage'] = 'style'

		return render(request, 'order_style.html', context)
	else:
		return redirect('headshot_error')


def ajax_headshot_add(request):
	if request.is_ajax() and request.method == 'GET':

		# decide whether need to input address
		has_package = False
		proceed = False

		data = {}
		# add to cart
		touchup = int(request.GET.get('touchup'))
		background = int(request.GET.get('background'))
		package = int(request.GET.get('package'))
		hs_id = request.session.get('hs_id')
		special_request = request.GET.get('special_request')
		subtotal = int(request.GET.get('subtotal'))

		hs = get_object_or_404(OriginalHeadshot, hash_id=hs_id)
		booking = hs.booking


		# do the total calculation here
		# touchup_val = 0
		# if request.session.get('proceed') and touchup == 1:
		# 	touchup_val = 1
		# elif touchup == 2:
		# 	touchup_val = 8
		# elif touchup == 3:
		# 	touchup_val = 10
		# elif touchup == 4:
		# 	touchup_val = 14


		package_val = 0
		if package == 2:
			package_val = 3
		elif package == 3:
			package_val = 9
		elif package == 4:
			package_val = 35
		elif package == 5:
			package_val = 30

		total = subtotal + package_val

		N = 8
		hash_id = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

		# create purchase instance
		hp = HeadshotPurchase(
			image=hs,
			raw_url=hs.raw_url,
			touchup=touchup,
			background=background,
			package=package,
			total=total,
			special_request=special_request,
			hash_id=hash_id,
			)
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)

				# check if the orders contain packages
				if not order.object.package == 1:
					has_package = True
				if order.object.total == 0:
					proceed = True

			orders.append(hp)
			has_package = has_package or not hp.package == 1
			proceed = proceed or hp.total == 0
		else:
			orders = [hp]
			proceed = hp.total == 0

		# populate the cart
		request.session['order'] = serializers.serialize('json', orders)


		request.session['proceed'] = HeadshotOrder.objects.filter(booking=booking).exists() or proceed

		print 'proceed in view',
		print request.session['proceed']


		data['orders'] = serializers.serialize('json', orders[::-1])
		data['total'] = int(sum(a.total for a in orders))
		data['has_package'] = has_package

		return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_headshot_remove(request):
	if request.is_ajax() and request.method == 'GET':
		data = {}

		id = request.GET.get('hash_id')

		# detect whether the one deleted is free
		clean_free = False
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):

				if not order.object.hash_id == id:
					orders.append(order.object)
				else:
					if order.object.total == 0:
						request.session['proceed'] = False
						clean_free = True


		data['total'] = int(sum(a.total for a in orders))
		data['empty'] = len(orders) == 0
		data['clean_free'] = clean_free
		request.session['clean_free'] = clean_free
		request.session['order'] = serializers.serialize('json', orders)
		# request.session['proceed'] = request.session.get('order')

		return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_keepsake_add(request):
	if request.is_ajax() and request.method == 'GET':
		data = {}

		id = request.GET.get('hash_id')
		keepsake_id = request.GET.get('keepsake')
		value = request.GET.get('value')

		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):

				if order.object.hash_id == id:
					order.object.package = keepsake_id
					order.object.total = str(int(order.object.total) + int(value))
				orders.append(order.object)
				print order.object

		request.session['order'] = serializers.serialize('json', orders)


		return HttpResponse(json.dumps(data), content_type='application/json')


def headshot_print_frame(request):
	if request.session.has_key('booking') and request.method == 'GET':

		touchup = request.GET.get('touchup')
		request.session['touchup'] = int(touchup)

		if not int(touchup) == 4:
			if request.session.get('special_request'):
				del request.session['special_request']

		special_request = request.GET.get('special_request')
		if special_request:
			request.session['special_request'] = special_request

		background = request.GET.get('background')
		request.session['background'] = int(background)

		print request.session['touchup']
		print request.session['background']
		if request.session.get('special_request'):
			print request.session['special_request']


		# show my cart
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)

		order_total = sum(a.total for a in orders)

		context = {
			'title_text': 'Select Package',
			'myheadshot': 1,
			'orders': orders,
			'order_total': order_total,
			'hs_id': request.session['hs_id'],
			'touchup': request.session['touchup'],
			'background': background,
			'cart': request.session.get('cart'),
		}

		# set stage
		request.session['stage'] = 'print'

		return render(request, 'order_print_frame.html', context)
	else:
		return redirect('headshot_error')


def headshot_review(request):
	if request.session.has_key('booking') and request.method == 'GET':
		
		request.session['package'] = int(request.GET.get('package'))


		# if request.GET.get('subtotal'):
		# 	request.session['total'] += int(request.GET.get('subtotal'))

		# for displaying the headshot image
		hs = get_object_or_404(OriginalHeadshot, hash_id=request.session.get('hs_id'))

		# calculate the total here
		touchup_val = 0
		if request.session.get('proceed') and request.session.get('touchup') == 1:
			touchup_val = 1
		elif request.session.get('touchup') == 2:
			touchup_val = 8
		elif request.session.get('touchup') == 3:
			touchup_val = 10
		elif request.session.get('touchup') == 4:
			touchup_val = 14


		package_val = 0
		if request.session.get('package') == 2:
			package_val = 3
		elif request.session.get('package') == 3:
			package_val = 9
		elif request.session.get('package') == 4:
			package_val = 35
		elif request.session.get('package') == 5:
			package_val = 30

		request.session['total'] = touchup_val + package_val

		hp = HeadshotPurchase(
			image=hs,
			touchup = request.session.get('touchup'),
			background = request.session.get('background'),
			package = request.session.get('package'),
			total = request.session.get('total'),
			special_request = request.session.get('special_request'),
			)

		# show my cart
		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)

		context = {
			'myheadshot': 1,
			'title_text': 'Review',
			'orders': orders,
			'booking': request.session.get('booking'),
			'cart': request.session.get('cart'),
			'order': hp,
		}

		# set stage
		request.session['stage'] = 'review'

		return render(request, 'order_review.html', context)
	else:
		return redirect('headshot_error')


def headshot_checkout(request):

	if request.session.has_key('booking') and request.method == 'GET':


		# keep track if physical address is needed
		has_package = False

		orders = []
		if request.session.has_key('order'):
			for order in serializers.deserialize('json', request.session.get('order')):
				orders.append(order.object)
				# TODO
				if not order.object.package == 1:
					has_package = True

		else:
			# redirect to error page
			return redirect('headshot_error')


		total = sum(a.total for a in orders)

		# keep track if the order total is 0, skip stripe
		free = total == 0

		# print orders
		context = {
			'myheadshot': 1,
			'title_text': 'Checkout',
			'has_package': has_package,
			'free': free,
			'orders': orders[::-1],
			'stripe_total': total * 100, # stripe
			'total': total,
			'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
			'myheadshot_checkout': 1,
		}

		# set stage
		# request.session['stage'] = 'checkout'

		return render(request, 'order_checkout.html', context)
	else:
		return redirect('headshot_error')


def headshot_complete(request):
	context = {
		'myheadshot': 1,
		'title_text': 'Thank you',
	}

	# get the order detail to generate email info
	booking_id = request.session.get('booking')

	print 'booking_id: ' + str(booking_id)

	b = Booking.objects.filter(hash_id=booking_id).order_by('-timestamp')[0]

	print 'booking found!'

	confirmation_content = ''
	sum = 0
	orders = []
	for order in serializers.deserialize('json', request.session.get('order')):
		orders.append(order.object)
		sum += order.object.total
		raw_url = order.object.image.raw_url

		special_request = ''
		if order.object.special_request:
			special_request = '<br>Special Request: ' + str(order.object.special_request)

		confirmation_content += '<img src="' + raw_url + '" width="150px"><br>' + 'Style: ' + order.object.get_touchup_display() + '<br>Background: ' + order.object.get_background_display() + '<br>Keepsakes: ' + order.object.get_package_display() + special_request+ '<br>Subtotal: $' + str(order.object.total) + '<br><br>'

	confirmation_content = confirmation_content + '<br><span style="font-size:1.5em; color: #c94848; font-weight: bold;">Total: $' + str(sum) + '</span><br>'

	# just to print out
	print str(booking_id) + ' ' + confirmation_content

	# free
	if request.GET.get('free'):

		print 'Free!'
		ho = HeadshotOrder(
			booking=b,
			total=sum,
			)	
		ho.save()
		for o in orders:
			o.order = ho
			o.charged = True
			o.copy_to_tbr()
			super(HeadshotPurchase, o).save()
		b.order_delivery_email(confirmation_content)

		# flush all the shit, not all the shit but orders
		if request.session.has_key('order'):
			del request.session['order']
		if request.session.has_key('hs_id'):
			del request.session['hs_id']
		# request.session.flush()

		return render(request, 'order_complete.html', context)


	# # test
	# for order in orders:
	# 	print order.image
	# 	print order.raw_url
	# 	print order.touchup

	# charge 
	if request.method == 'POST':

		print 'Charging!'

		token = request.POST.get('token')
		total = request.POST.get('total')
		address = request.POST.get('address')

		# shipping
		express = request.POST.get('express')

		# add shipping fee
		if express:
			sum += 3


		# flush all the shit
		if request.session.has_key('order'):
			del request.session['order']
		if request.session.has_key('hs_id'):
			del request.session['hs_id']
		# request.session.flush()

		try:
			charge = stripe.Charge.create(
				amount = total,
				currency="usd",
				source=token,
				description="Bryte Headshot"
			)
		except stripe.error.CardError, e:
			# charge erro, redirect to checkout page
			context['msg'] = 'There\'s a problem charging your card. Your card was not charged. Please try again.'
			print 'Charging Error'

			# create the ho and hp instances as well
			ho = HeadshotOrder(
				booking=b,
				total=sum,
				address=address,
				express_shipping=express,
				)

			try:
				ho.save()
			except Exception, e:
				print 'order instance fails to create ' + str(e)
				pass

			for o in orders:
				o.order = ho
				try:
					super(HeadshotPurchase, o).save()
				except Exception, e:
					print 'purchase instance fails to create ' + str(e)
					pass	

			return render(reverse('headshot_checkout'))
		else:

			# generate email info, send the email
			b.order_delivery_email(confirmation_content)

			


			# create image order instance
			ho = HeadshotOrder(
				booking=b,
				total=sum,
				address=address,
				express_shipping=express,
				)

			try:
				ho.save()
			except Exception, e:
				print 'order instance fails to create ' + str(e)
				pass
			else:
				print 'order instance successfully created ' + str(b.email)

			# create image purchase instance
			# copied image in PROD to TBR
			for o in orders:
				print o.image

				o.order=ho
				o.charged=True

				# call super method to save the instance to avoid pk conflict in postgres
				try:
					super(HeadshotPurchase, o).save()
				except Exception, e:
					print 'purchase instance fails to create ' + str(e)
					
				else:
					print 'purchase instance successfully created ' + str(b.email)

				o.copy_to_tbr()

				# o.order = ho
				# o.charged = True
				# copy to tbr
				# o.copy_to_tbr()

				# try:
				# 	o.save()

				# else:
				# 	print 'purchase instance successfully created ' + str(b.email)
			return render(request, 'order_complete.html', context)


def headshot_error(request):
	context = {
		'myheadshot': 1,
		'title_text': 'Time out',
	}
	if request.GET.get('hs_email') and request.method=='GET':

		try:
			b = Booking.objects.filter(email=str(request.GET.get('hs_email'))).last()
		except Exception, e:
			context['msg'] = 'Sorry we don\'t have your email on file, are you entering the correct email?'
		else:
			hash_id = b.hash_id
			url = reverse('headshot_index') + '?id=' + hash_id
			print url
			return redirect(url)

	return render(request, 'order_error.html', context)


def headshot_expire(request):
	context = {
		'myheadshot': 1,
		'title_text': 'The photos are expired'
	}

	return render(request, 'order_expire.html', context)