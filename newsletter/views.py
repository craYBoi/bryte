from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import stripe
import os
import dropbox

import json
from .forms import SignUpForm
from photographer.models import Photographer
from .models import Price, PriceFeature, ContactSale, ContactHelp, FamilyContact
from book.models import TimeSlot, NextShoot
from careerlab.models import Booking, ImagePurchase, HeadshotImage



stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def home(request):

	form = SignUpForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		# print instance
		instance.save()

	title = 'Bryte Photo | Custom and friendly headshot photography sessions for $20'

	timeslots = TimeSlot.objects.filter(is_available=True).order_by('time')
	next_shoot = NextShoot.objects.first()


	context = {
		'timeslots': timeslots,
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
		'title_text': title,
		'next_shoot': next_shoot,
		'is_index': 1,
	}
	return render(request, "index.html", context)


def about(request):
	context = {
		'title_text': 'about',
	}

	return render(request, "about.html", context)


def package(request):
	# filter get request to get price packages
	packages = Price.objects.all().order_by('price')
	if request.method == "GET":
		photo_video = request.GET.get('photo_video')
		re_sb = request.GET.get('re_sb')

		is_photo = False
		print photo_video
		if photo_video and re_sb:
			if photo_video=='photography':
				is_photo = True
			
			packages = Price.objects.filter(is_photography=is_photo).order_by('price')
			packages = packages.filter(category=re_sb).order_by('price')


	# create a list of a list of packages
	# 0 - House Tour, 1 - Advertising Video, 2 - Promotional Video
	# 3 - House Photo, 4 - Small Business Marketing Photo, 5 - Product Photo
	list_of_packages = {}
	for package in packages:
		if package.shared_title in list_of_packages:
			list_of_packages[package.shared_title].append(package)
		else:
			list_of_packages[package.shared_title] = [package]


	context = {
		'title_text': 'Packages',
		'packages': packages,
		'packages_list': list_of_packages,
	}

	return render(request, "package.html", context)



def become_photographer(request):
	context = {
		'title_text': 'Become a Student Photographer'
	}

	return render(request, 'become_photographer.html', context)


def select_photographer(request):
	context = {
		'title_text': 'How do we select our photographers'
	}

	return render(request, 'select_photographer.html', context)

def faq(request):
	context = {
		'title_text': 'FAQs'
	}
	

	return render(request, 'faq.html', context)


def legal(request):
	context = {
		'title_text': 'Legal Documentations'
	}

	return render(request, 'legal_stuff.html', context)



def clients(request):
	context = {
		'title_text': 'Our Clients | Bryte Photo Headshots',
		'is_clients': 1,
	}

	url = request.get_full_path()
	index = url[::-1][1:].index('/')
	url = url[-index-1:-1]

	if url == 'ric':
		return render(request, 'landing_clients_ric.html', context)
	

	return render(request, 'landing_clients.html', context)


def contact(request):
	context = {
		'title_text': 'Contact Sales | Bryte Photo Headshots',
		'is_contact': 1,
	}
	return render(request, 'landing_contact.html', context)


def help(request):
	context = {
		'title_text': 'Contact Help | Bryte Photo Headshots',
		'is_contact': 1,
	}
	return render(request, 'landing_help.html', context)


def signup_template(request):
	context = {
		'title_text': 'Signup Template',
		'brown_careerlab': 1,
	}	
	return render(request, 'landing_signup_template.html', context)


def test(request):
	context = {
		'title_text': 'Internal Test',
	}
	return render(request, 'test.html', context)


def test2(request):
	context = {
		'title_text': 'Internal Test 2',
		'myheadshot': 1,
	}
	return render(request, 'test2.html', context)


def family(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		email = request.POST.get('email')
		family_email = request.POST.get('family_email')

		try:
			b = get_object_or_404(Booking, email=email)
			try:
				f = FamilyContact.objects.create(
						email=email,
						book = b,
						family_email=family_email
					)
			except Exception, e:
				data['msg'] = 'Something went wrong, Please try again'
				pass
			else:
				# send the email and stuff
				pass
		except Exception, e:
			data['msg'] = 'We haven\'t seen that email before! Are you sure that this is the email you booked your headshot with?'
			pass
		else:
			data['msg'] = 'We got the email you entered. We will send out notification when your headshots are available'
		return HttpResponse(json.dumps(data), content_type='application/json')

	context = {
		'title_text': 'Family Free Headshot | Bryte Photo Headshots',
	}
	return render(request, 'landing_family.html', context)


def sales(request):
	context = {
		'title_text': 'Getting extra headshots',
	}
	return render(request, 'landing_sales.html', context)


def ajax_contact(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		name = request.POST.get('name')
		email = request.POST.get('email')
		category = request.POST.get('category')
		org_name = request.POST.get('orgname')
		amount = request.POST.get('amount')
		question = request.POST.get('question')
		phone = request.POST.get('phone')

		first_name = name.strip().split(' ')[0]

		# create database instance
		try:
			c = ContactSale.objects.create(name=name, email=email, organization=org_name, amount=amount, phone=phone)
		except Exception, e:
			print 'Fail to create instance'
			data['msg'] = 'There\'s an error signing up. Please try again.'
			raise e
		else:
			# send the email
			data['msg'] = 'Thank you ' + first_name + ' for contacting us! We will get to you as soon as we can!'

			msg_body = 'Contact Sales Information:\n\nName: ' + str(name) + '\nEmail: ' + str(email) + '\nPhone: ' + str(phone) + '\nOrganization: ' + str(org_name) + '\nCategory: ' + str(category) + '\nAmount of Headshots Estimate: ' + str(amount) + '\nQuestion & Request: ' + str(question) + '\n\nBest,\nBryte Photo Team'

			try:
				send_mail('New Contact Sales Inquiry!', msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [settings.EMAIL_HOST_USER], fail_silently=False)
			except Exception, e:
				print 'Email Not Sent!'
				raise e

		return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_help(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		name = request.POST.get('name')
		email = request.POST.get('email')
		question = request.POST.get('question')

		first_name = name.strip().split(' ')[0]

		# create database instance
		try:
			c = ContactHelp.objects.create(name=name, email=email, question=question)
		except Exception, e:
			print 'Fail to create instance'
			data['msg'] = 'There\'s an error signing up. Please try again.'
			raise e
		else:
			# send the message
			data['msg'] = 'Thank you ' + first_name + ' for contacting us! We will get to you as soon as we can!'

			msg_body = 'Contact Help Information:\n\nName: ' + str(name) + '\nEmail: ' + str(email) + '\nQuestion & Request: ' + str(question) + '\n\nBest,\nBryte Photo Team'

			# send the email
			try:
				send_mail('New Contact Help!', msg_body, 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [settings.EMAIL_HOST_USER], fail_silently=False)
			except Exception, e:
				print 'Email Not Sent!'
				raise e

		return HttpResponse(json.dumps(data), content_type='application/json')



def retrieve(request):
	context = {
		'title_text': 'Retrive your headshot | Bryte Photo',
	}
	return render(request, 'landing_retrieve.html', context)


def ajax_retrieve(request):
	if request.is_ajax() and request.method == 'POST':
		data = {}
		# do the trimming in case people paste it with spacebar
		unique_id = request.POST.get('unique_id').strip()

		try:
			booking = get_object_or_404(Booking, hash_id=unique_id)
		except Exception, e:
			pass
		else:
			email = booking.email
			dropbox_folder_url = booking.dropbox_folder

			# retrieve images from Dropbox
			deliverable_thumbs = booking.retrieve_image(deliverable_thumb=True)
			deliverable_originals = booking.retrieve_image(deliverable_original=True)
			wa_originals = booking.retrieve_image(wa_original=True)
			wa_thumbs = booking.retrieve_image(wa_thumb=True)

			data['deliverable_originals'] = deliverable_originals
			data['deliverable_thumbs'] = deliverable_thumbs
			data['wa_originals'] = wa_originals
			data['wa_thumbs'] = wa_thumbs


		return HttpResponse(json.dumps(data), content_type='application/json')
	else:
		raise Http404


@csrf_exempt
def test_retrieve(request):
	context = {
		'title_text': 'Retrive your headshot | Bryte Photo',
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
		'myheadshot': 1,
	}

	# if request.method == 'POST':
	if request.is_ajax():
		data = {}
		print request.POST
		# just for the single download
		if request.POST.get('is_download'):
			copied = False
			pk = request.POST.get('pk')
			try:
				img = get_object_or_404(HeadshotImage, pk=pk)
			except Exception, e:
				data['msg'] = 'We have some problems delivering the photos, we are solving that right now.'
				raise e
			else:	
				data['msg'] = 'Congratulations on your free Linkedin headshot!  You will receive it via email shortly.'
				# send the email
				copied = img.copy_to_upgrade()

				img.book.photo_delivery_email()
				is_delivered = True

				try:
					ImagePurchase.objects.create(
						image=img,
						option='',
						value='0',
						email=img.book.email,
						charge_successful=True,
						is_delivered=is_delivered,
						is_copied=copied,
					)
				except Exception, e:
					print '[Failed] Create download instance'

			return HttpResponse(json.dumps(data), content_type='application/json')


		try:
			purchases = json.loads(request.POST.get('purchases'))
		except Exception, e:
			raise e
		else:
			print purchases
			# charge first
			token = request.POST.get('token')
			total = request.POST.get('total')
			subtotal = request.POST.get('subtotal')
			discount = float(subtotal) - float(total)

			# for fullsize and premium
			if str(float(total))=='0':
				total = purchases[0].get('value')

			print purchases[0].get('value')
			print total

			try:
				charge = stripe.Charge.create(
					amount = int(float(total) * 100),
					currency="usd",
					source=token,
					description="Bryte Photo Headshot"
				)
			except stripe.error.CardError, e:
				# update the status in purchase
				charge_successful = False

				data['msg'] = 'There\'s an error charging your card. Please provide another card'
			else:
				
				# populate the purchases
				charge_successful = True

				data['msg'] = 'Congratulations on your purchase! We will send you a confirmation email explaining when you will receive your purchase.'

			# send out upgrade confirmation email
			confirmation_content = ''

			for purchase in purchases:
				special_note = ''

				img = get_object_or_404(HeadshotImage, pk=purchase.get('img_id'))
				if img.is_fav or img.is_top or img.is_portrait:
					special_note = 'Expect to receive your headshot via email right away'
				else:
					special_note = 'Expect to receive your headshot via email within 48 hours.'

				option=purchase.get('option')
				option_text = ''
				if option == 'fh':
					option_text = 'Free Standard LinkedIn headshot'
				elif option == 'pu':
					option_text = 'Professional LinkedIn headshot'
				elif option == 'ph':
					option_text = 'Extra Professional Headshot'
				elif option == 'pp':
					option_text = 'Premium Portrait'

				value=purchase.get('value')


				confirmation_content += '1 ' + option_text + ' ---------------- $' + str(value) + '<br>' + special_note + '<br>'


			confirmation_content += '<br><br>Subtotal: $' + str(subtotal) + '<br>Discount: $' + str(discount) + '<br><br><span style="font-size:1.5em; color: #c94848; font-weight: bold;">Total: $' + str(total) + '</span>'
			# send it
			img.book.order_delivery_email(confirmation_content)



			# top headshots delivery
			ips = []
			for purchase in purchases:
				# is_copied
				copied = False
				# find the Image intance first
				try:
					img = get_object_or_404(HeadshotImage, pk=purchase.get('img_id'))
				except Exception, e:
					raise e
				else:
					try:
						copied = img.copy_to_upgrade()
					except Exception, e:
						# change later
						print '[FAILED] Copy To Upgrade'

					try:
						ip = ImagePurchase.objects.create(
							image=img,
							option=purchase.get('option'),
							value=purchase.get('value'),
							email=img.book.email,
							charge_successful=charge_successful,
							is_delivered=False,
							is_copied=copied,
						)

					except Exception, e:
						print '[FAILED] Create purchase instance'
					else:
						ips.append(ip)
						print '[SUCCESS] Create purchase instance'

			# only send one delivery email
			# is_delivered not true when cannot be delivered right away, extra photos
			if img.book.photo_delivery_email():
				for ip in ips:
					img = ip.image
					if img.is_fav or img.is_top or img.is_portrait:
						ip.is_delivered = True
						ip.save()



		return HttpResponse(json.dumps(data), content_type='application/json')
	if request.method == 'GET':
		try:
			unique_id = request.GET.get('id').strip()
		except Exception, e:
			return render(request, 'test_retrieve.html', context)
		try:
			b = get_object_or_404(Booking, hash_id=unique_id)
			# grab all the image from booking
			headshots = b.headshotimage_set.all().order_by('pk')
		except Exception, e:
			context['msg'] = 'Did you enter the right ID? Check your email to make sure.'
			pass
		else:
			# break down the deliverable, premium and fullsize
			if headshots:
				context['booking'] = b
				context['headshots'] = headshots
				context['raw_fav'] = [hs for hs in headshots if hs.is_raw and hs.is_fav][0]
				context['edited_fav'] = [hs for hs in headshots if hs.is_fav and not hs.is_raw][0]
				context['raw_top'] = [hs for hs in headshots if hs.is_top and hs.is_raw][0]
				# context['edited_top'] = [hs for hs in headshots if hs.is_top and not hs.is_raw][0]
				context['edited_portrait'] = [hs for hs in headshots if hs.is_portrait][0]
				context['extras'] = [hs for hs in headshots if not hs.is_fav and not hs.is_top and not hs.is_portrait and hs.is_raw]
			else:
				context['msg'] = 'Your headshots are not ready yet! They should be good to go soon!'

	return render(request, 'test_retrieve.html', context)


