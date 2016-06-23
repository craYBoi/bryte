from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, HttpResponse

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
	dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)

	root = '/'
	folder = 'Deliverables'
	name = 'CareerLAB1'
	path = os.path.join(root, folder, name)

	urls = []
	folders = dbx.files_list_folder(path).entries
	entry = folders[0]
	items = dbx.files_list_folder(entry.path_display).entries
	for item in items:
		sharing_link = dbx.sharing_create_shared_link(item.path_display, short_url=False, pending_upload=None)
		url = str(sharing_link.url)
		url = url[:-4]
		url += 'raw=1'
		urls.append(url)

	context['urls'] = urls

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
			c = ContactSale.objects.create(name=name, email=email,category=category, organization=org_name, amount=amount,question=question, phone=phone)
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


def test_retrieve(request):
	context = {
		'title_text': 'Retrive your headshot | Bryte Photo',
		'publish_key': settings.STRIPE_PUBLISHABLE_KEY,
	}

	if request.method == 'POST':
		if request.is_ajax():
			data = {}
			print request.POST
			try:
				purchases = json.loads(request.POST.get('purchases'))
			except Exception, e:
				raise e
			else:
				# charge first
				token = request.POST.get('token')
				total = request.POST.get('total')

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

					data['msg'] = 'Thanks for the order! We will send a confirmatiln email to you and will deliver the order in 48 hours!'

				for purchase in purchases:
					# find the Image intance first
					try:
						img = get_object_or_404(HeadshotImage, pk=purchase.get('img_id'))
					except Exception, e:
						raise e
					else:
						is_delivered = False
						# send the email as a method of Purchase
						if img.is_fullsize:
							fullsize = img.book.headshotimage_set.filter(is_fullsize=True, is_watermarked=False)[0]

							img.book.dropbox_delivery_email(fullsize.original_url)
							is_delivered = True

						if img.is_premium:
							premium = img.book.headshotimage_set.filter(is_premium=True, is_watermarked=False)[0]

							img.book.dropbox_delivery_email(premium.original_url)
							is_delivered = True

						try:
							ImagePurchase.objects.create(
								image=img,
								option=purchase.get('option'),
								value=purchase.get('value'),
								email=img.book.email,
								address=purchase.get('address'),
								request=purchase.get('request'),
								charge_successful=charge_successful,
								is_delivered=is_delivered,
							)

						except Exception, e:
							print 'create purchase fail'
							raise e
						else:
							print 'create successfully'
			return HttpResponse(json.dumps(data), content_type='application/json')
		else:
			unique_id = request.POST.get('retrieve_search').strip()
			try:
				b = get_object_or_404(Booking, hash_id=unique_id)
				# grab all the image from booking
				headshots = b.headshotimage_set.all().order_by('pk')
			except Exception, e:
				context['msg'] = 'Did you enter the right ID? Check your email to make sure.'
			else:
				# break down the deliverable, premium and fullsize
				context['deliverable'] = [hs for hs in headshots if hs.is_deliverable][0]
				context['premium'] = [hs for hs in headshots if hs.is_premium and hs.is_watermarked][0]
				context['fullsize'] = [hs for hs in headshots if hs.is_fullsize and hs.is_watermarked][0]
				context['extra'] = [hs for hs in headshots if hs.is_extra()]

	return render(request, 'test_retrieve.html', context)


