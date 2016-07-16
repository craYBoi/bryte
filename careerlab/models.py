from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from uuid import uuid4
from datetime import datetime, timedelta
from photographer.models import Photographer
from random import SystemRandom
import string

import os
import json
import dropbox
import sendgrid
from sendgrid import SendGridError, SendGridClientError, SendGridServerError


# call sendgrid api
sg = sendgrid.SendGridClient(settings.SENDGRID_KEY, None, raise_errors=True)
sgapi = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_KEY)
BOOKING_CONFIRMATION_ID = '71ff210a-f5f5-4c3a-876a-81d46197ed77'
DB_REMINDER_ID = 'ef27b980-d764-4ee3-8ffc-e8cd7f9377d8'
MY_HEADSHOT_1_ID = 'd2750257-04b4-4e24-a785-aa34a7942606'
PHOTO_DELIVERY_ID = '3ee6fdaa-0e23-4914-8f53-c06265dbbd57'
ORDER_DELIVERY_ID = 'c8690ffe-8ca3-4531-b46e-dbf747bdc18b'
PASSPORT_ID = 'daa1b2ab-9d4d-4023-8546-d2bd88b73c02'
RIC_NOT_PAYING_ID = '91554ce0-b80a-4c1f-ad12-0a3ec606e29e'
SURVEY_EMAIL_TO_RIC_ID = '6e9cb0a1-535b-42dc-9279-4b9d23f19a1a'
SURVEY_EMAIL_TO_BROWN_ID = '5c562a0c-25f6-4151-a81a-99089ea00d61'


# max sessions per time slot
MAX_VOLUMN = 4


class Nextshoot(models.Model):
	photographer = models.ForeignKey(Photographer, related_name='nextshoot_photographer')
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	name = models.CharField(max_length=100, blank=True, null=True)
	school = models.CharField(max_length=60, default='not assigned')
	date = models.DateField(default=timezone.now)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ('-timestamp',)


	# override save method to first create folder
	# Create PROD Shoot Folder - customer
	# Create PHOTO Shoot Folder - photographer
	# Create TOUCHUP Shoot Folder - photoshopper
	def save(self, *args, **kwargs):
		name = self.location + ' - ' + str(self.date.strftime('%Y-%m-%d'))

		# populate the shoot name field
		self.name = name
		super(Nextshoot, self).save(*args, **kwargs)

		# create shoot folder in PROD
		self.create_prod_folder()

		# create shoot folder in PHOTO
		self.create_photo_folder()

		# create shoot folder in TOUCHUP
		self.create_touchup_folder()


	def __unicode__(self):
		return self.name


	# need to return all the timeslots
	# since it's needed when the shoot is closed
	def get_date_string(self):
		timeslots = self.timeslot_set.all()
		if timeslots:
			return str(timeslots.first().time.strftime('%B %-d'))
		return None


	def get_time_interval_string(self):
		timeslots = self.timeslot_set.all()
		if timeslots:
			a = sorted(timeslots, reverse=False, key=lambda timeslot: timeslot.time)
			str_time_start = a[0].time.strftime('%-I:%M %p')
			time_end = a[-1].time + timedelta(seconds=600)
			str_time_end = time_end.strftime('%-I:%M %p')
			return str_time_start + ' - ' + str_time_end
		return None


	# create dropbox folder for Shoot
	def create_prod_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		root_folder = settings.DROPBOX_PATH
		folder_path = os.path.join(root_folder, self.name)

		try:
			dbx.files_create_folder(folder_path)
		except Exception, e:
			print e
			return 0
		else:
			return 1


	# create dropbox folder for photographers for shoot
	def create_photo_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		root_folder = settings.DROPBOX_PHOTO
		folder_path = os.path.join(root_folder, self.name)

		try:
			dbx.files_create_folder(folder_path)
		except Exception, e:
			print e
			return 0
		else:
			return 1


	# create shoot folder for photoshoppers
	# create a subfolder called Edited for photoshoppers to put in deliverables. Should be 3 versions for each single favorite raw photo
	# _pf -> professional headshot
	# _pt -> professional portrait
	# _s -> standard_headshot
	def create_touchup_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		root_folder = settings.DROPBOX_TOUCHUP
		folder_path = os.path.join(root_folder, self.name)

		try:
			dbx.files_create_folder(folder_path)
		except Exception, e:
			print e
			return 0
		else:
			# create Edited folder inside for photoshoppers
			edited_folder_path = os.path.join(folder_path, 'Edited')
			try:
				dbx.files_create_folder(edited_folder_path)
			except Exception, e:
				print e
				return 0
			else:
				return 1	


	# migrate favs in PHOTO to TOUCHUP for photoshopper for this shoot
	def migrate_photo_to_touchup(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		photo_folder_path = os.path.join(settings.DROPBOX_PHOTO, self.name)

		try:
			items = dbx.files_list_folder(photo_folder_path).entries
		except Exception, e:
			raise e
		else:
			for item in items:
				path = item.path_lower
				email = item.name
				try:
					images = dbx.files_list_folder(path).entries
					# find the one with _fav
					# list image here and concat with email with '+', get rid of _fav and ready to copy to touchup folder
				except Exception, e:
					raise e
				else:
					# find the one with fav
					try:
						fav = [image for image in images if os.path.splitext(image.name)[-2].split('_')[-1] == 'fav'][0]
					except Exception, e:
						print 'Fav not found in folder'
						raise e
					else:
						# copy files
						# get rid of _fav and add email address with '+' as splitter
						name = '+'.join([email, fav.name.replace('_fav', '')])

						# copy path to touchup folder
						copy_path = os.path.join(settings.DROPBOX_TOUCHUP, self.name, name)
						try:
							dbx.files_copy(fav.path_lower, copy_path)
						except Exception, e:
							print 'copy image failed'
							pass
						else:
							print 'Found fav and copied to TOUCHUP'
			return 1


	# PHOTO check script

	# TOUCHUP check script

	# compress the image in TOUCH Edited

	# migrate image from TOUCH Edited to PROD/TEST Edited 

	# migrate raw image from PHOTO to PROD/TEST RAW


	def send_reminder(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]
		
		count = 0
		for booking in bookings:
			if(booking.db_reminder_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def close_shoot(self):
		self.active = False
		super(Nextshoot, self).save()


	def send_replacement(self):
		timeslots = self.timeslot_set.all()
		num_slots_available = MAX_VOLUMN * len(timeslots) - sum(e.current_volumn for e in timeslots)

		num_ppl_to_notify = 8 * num_slots_available
		signups = Signup.objects.filter(notified=False).order_by('timestamp')

		if len(signups) > num_ppl_to_notify:
			signups = signups[:num_ppl_to_notify]

		count = 0
		for e in signups:
			count += 1
			name = e.name
			email = e.email
			title = 'New headshot sessions are opened!'
			msg = 'Hi ' + name + ',\n\nGreat news! There are now ' + str(num_slots_available) + ' headshots sessions available! We are shooting tomorrow afternoon between 12:30 pm - 3:30 pm on the first floor of Brown CareerLAB. Book your session here:\n\nwww.brytephoto.com/CareerLAB\n\nBest, \nCareerLAB and the Team Bryte'
			try:
				send_mail(title, msg, 'Bryte and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				raise e
			else:
				e.notified = True
				e.save()
				print '[SENT] ' + email
		print str(count) + ' emails sent'


	def notify_all(self):
		signups = Signup.objects.filter(notified=False).order_by('timestamp')

		for e in signups:
			name = e.name
			email = e.email
			title = 'Free LinkedIn Headshots with Bryte Photo at CareerLAB!'
			msg = 'Hi ' + name + ',\n\nGreat news! Bryte Photo is partnering with CareerLAB to offer free Linkedin headshots to all students this Friday, May 13th at Brown CareerLAB. We will be shooting between 12:30pm - 3:30pm on the first floor of CareerLAB. Book a session and learn more about Bryte Photo here:\n\nwww.brytephoto.com/CareerLAB\n\nBest, \nCareerLAB and the Bryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				raise e
			else:
				print '[SENT] ' + email


	def notify_some(self, email_name):
		signups = Signup.objects.filter(notified=False).order_by('timestamp')
		email_list = [e.email for e in signups]
		index = email_list.index(email_name)
		signups = signups[index+1:]

		for e in signups:
			name = e.name
			email = e.email
			title = 'Free LinkedIn Headshots with Bryte Photo at CareerLAB!'
			msg = 'Hi ' + name + ',\n\nGreat news! Bryte Photo is partnering with CareerLAB to offer free Linkedin headshots to all students this Friday, May 13th at Brown CareerLAB. We will be shooting between 12:30pm - 3:30pm on the first floor of CareerLAB. Book a session and learn more about Bryte Photo here:\n\nwww.brytephoto.com/CareerLAB\n\nBest, \nCareerLAB and the Bryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				raise e
			else:
				print '[SENT] ' + email


	# temp method integrated with dropbox
	def send_delivery(self):
		# filter out the no shows
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]
		
		count = 0
		for booking in bookings:
			if(booking.my_headshot_1_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	# temp method integrated with dropbox
	def update_showups(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]

		count = 0
		for booking in bookings:
			if(booking.update_showup()):
				count += 1
		print str(count) + ' people showed up!'


	def create_images(self, raw=False, edited=False, fav=False, top=False, portrait=False, all=False):
		bookings = [e for elem in self.timeslot_set.filter.all() for e in elem.booking_set.filter(show_up=True)]

		for booking in bookings:
			# this already handles the empty folder
			booking.create_image(raw=raw, edited=edited, fav=fav, top=top, portrait=portrait, all=all)


class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	notified = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	shoot = models.ForeignKey(Nextshoot, blank=True, null=True)
	program_progress = models.CharField(max_length=30, blank=True, null=True)
	area_of_study = models.CharField(max_length=40, blank=True, null=True)
	professional_path = models.CharField(max_length=40, blank=True, null=True)

	def __unicode__(self):
		return self.name + ' ' + self.email



class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)
	shoot = models.ForeignKey(Nextshoot)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')

		# overbook trick
		slot_left = min(MAX_VOLUMN - 1, MAX_VOLUMN - self.current_volumn) 

		slot_left_str = ' ------ ' + str(slot_left) + '/3 headshot sessions left'
		time_format += slot_left_str
		if time_format[0] == '0':
			return time_format[1:]
		return time_format

	def increment(self):
		# this should not be happening
		if not self.is_available:
			print 'this should not be happening'

		if self.current_volumn < MAX_VOLUMN and self.is_available:
			self.current_volumn += 1
			if self.current_volumn == MAX_VOLUMN:
				self.is_available = False
			self.save()

	def reset(self):
		self.is_available = True
		self.current_volumn = 0

	def restore_slot(self):
		self.is_available = True
		self.current_volumn -= 1
		self.save()



class Booking(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	timeslot = models.ForeignKey(Timeslot)
	hash_id = models.CharField(max_length=50, default='default')
	dropbox_folder = models.CharField(max_length=100, blank=True, null=True)
	upgrade_folder_path = models.CharField(max_length=100, blank=True, null=True)
	show_up = models.BooleanField(default=False)
	program_progress = models.CharField(max_length=30, blank=True, null=True)
	area_of_study = models.CharField(max_length=40, blank=True, null=True)
	professional_path = models.CharField(max_length=40, blank=True, null=True)


	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)

	# override save to add hashid upon creation
	def save(self, *args, **kwargs):
		# increment the timeslot
		self.timeslot.increment()

		N = 6
		self.hash_id = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

		# create booking folder in PROD
		self.create_dropbox_folder()

		# create booking folder in PHOTO
		self.create_dropbox_photo_folder()	

		super(Booking, self).save(*args, **kwargs)

	def cancel_order(self):
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		
		# open up 1 slot 
		ts.restore_slot()

		# add delete the corresponding dropbox
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		# also delete the PHOTO folder
		root_folder = settings.DROPBOX_PHOTO
		shoot_name = ts.shoot.name
		photo_path = os.path.join(root_folder, shoot_name, self.email)

		try:
			deleted_folder = dbx.files_delete(self.dropbox_folder)
			dbx.files_delete(photo_path)
		except Exception, e:
			print e
			pass

		self.delete()

	def generate_booking_link(self, school_url):
		return os.path.join(settings.SITE_URL, 'school', school_url)

	def generate_cancel_link(self):
		return settings.SITE_URL + reverse('careerlab_cancel_order') + '?order_id=' + str(self.hash_id)

	def tips_link(self):
		return settings.SITE_URL + reverse('careerlab_tips')

	def booking_confirmation_email(self):
		name = self.name
		first_name = name.split(' ')[0]
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school
		email = self.email


		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Your headshot booking confirmation') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id','71ff210a-f5f5-4c3a-876a-81d46197ed77')


		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(BOOKING_CONFIRMATION_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-timeslot-', str(timeslot))
		message.add_substitution('-location-', location)
		message.add_substitution('-cancel_link-', self.generate_cancel_link())

		# message.add_filter('ganalytics', 'enable', '1')
		# message.add_filter('ganalytics', 'utm_source', 'Booking Confirmation Email [GA]')
		# message.add_filter('ganalytics', 'utm_medium', 'email [GA]')
		# message.add_filter('ganalytics', 'utm_content', 'Confirm their booking [GA]')
		# message.add_filter('ganalytics', 'utm_campaign', 'Campaign Name! [GA]')

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
			# raise e
		else:
			print '[SENT] --- ' + str(email)


	def db_reminder_email(self):
		sent = False
		name = self.name
		first_name = name.split(' ')[0]
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school
		email = self.email

		school_url = ''
		if school == 'Community College of Rhode Island':
			school_url = 'ccriknight'
		elif school == 'Boston University':
			school_url = 'bu'
		else:
			school_url = 'brown'

		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(DB_REMINDER_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Tips for your headshot tomorrow') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', DB_REMINDER_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-time_slot-', str(timeslot))
		message.add_substitution('-location-', location)
		message.add_substitution('-cancel_link-', self.generate_cancel_link())
		message.add_substitution('-book_link-', self.generate_booking_link(school_url))

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def my_headshot_1_email(self):
		sent = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		hash_id = self.hash_id
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school


		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(MY_HEADSHOT_1_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]


		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')

		message.set_subject('Your free LinkedIn headshot is ready for download!')
 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')

		message.add_filter('templates','template_id', MY_HEADSHOT_1_ID)


		message.set_categories(category)

		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-unique_id-', hash_id)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send

	# upgrade confirmation email, takes in order detail
	def order_delivery_email(self, html_content):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school

		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(ORDER_DELIVERY_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Your super-awesome order from Bryte') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', ORDER_DELIVERY_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-order_detail-', html_content)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def photo_delivery_email(self):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		hash_id = self.hash_id		
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school

		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(PHOTO_DELIVERY_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Your purchase is ready for download!') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', PHOTO_DELIVERY_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-download_link-', self.upgrade_folder_path)
		message.add_substitution('-unique_id-', hash_id)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
			# raise e
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def ric_not_paying(self):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		hash_id = self.hash_id		
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school
		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(RIC_NOT_PAYING_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('New version of your Linkedin headshot') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', RIC_NOT_PAYING_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-download_link-', self.upgrade_folder_path)
		message.add_substitution('-unique_id-', hash_id)

		message.add_filter('subscriptiontrack','enable','1')
		message.add_filter('subscriptiontrack','replace','[unsubscribe]')

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
			# raise e
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def survey_email_to_ric(self):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school

		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(SURVEY_EMAIL_TO_RIC_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Get a $10 Amazon gift card for your feedback') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', SURVEY_EMAIL_TO_RIC_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def survey_email_to_brown(self):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school

		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(SURVEY_EMAIL_TO_BROWN_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('An opportunity to give back') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', SURVEY_EMAIL_TO_BROWN_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def passport_email(self):
		send = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		hash_id = self.hash_id		
		timeslot = self.timeslot
		shoot = timeslot.shoot
		location = shoot.location
		date = shoot.date
		school = shoot.school
		# get template, version name, and automatically add to category
		email_purpose = 'Error'
		version_number = 'Error'
		try:
			email_template = json.loads(sgapi.client.templates._(PASSPORT_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]
		
		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('New version of your Linkedin headshot') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', PASSPORT_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-download_link-', self.upgrade_folder_path)
		message.add_substitution('-unique_id-', hash_id)

		message.add_filter('subscriptiontrack','enable','1')
		message.add_filter('subscriptiontrack','replace','[unsubscribe]')

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
			# raise e
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	# create all the folders when sign up and get the upgrade link
	def create_dropbox_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		email = self.email
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		shoot_pk = ts.shoot.pk
		shoot = get_object_or_404(Nextshoot, pk=shoot_pk)
		shoot_name = shoot.name

		root_folder = settings.DROPBOX_PATH

		# upload path
		upload_folder_path = os.path.join(root_folder, shoot_name, email)

		# print upload_folder_path
		# create the folder
		try:
			dbx.files_create_folder(upload_folder_path)
		except Exception, e:
			print e
			# raise e
		else:
			# store the upload path in the Booking
			self.dropbox_folder = upload_folder_path

			# create the All and Deliverables subfolder
			EDITED_FOLDER = 'Edited'
			OTHER_FOLDER = 'Other'
			RAW_FOLDER = 'Raw'
			UPGRADE_FOLDER = 'Upgrade'

			edited_folder_path = os.path.join(upload_folder_path, EDITED_FOLDER)
			edited_fav_path = os.path.join(edited_folder_path, 'Fav')
			# edited_top_path = os.path.join(edited_folder_path, 'Top')
			edited_portrait_path = os.path.join(edited_folder_path, 'Top Portrait')
			edited_all_path = os.path.join(edited_folder_path, 'All')

			other_folder_path = os.path.join(upload_folder_path, OTHER_FOLDER)
			raw_folder_path = os.path.join(upload_folder_path, RAW_FOLDER)
			raw_fav_path = os.path.join(raw_folder_path, 'Fav')
			raw_top_path = os.path.join(raw_folder_path, 'Top')
			raw_all_path = os.path.join(raw_folder_path, 'All')

			upgrade_folder_path = os.path.join(upload_folder_path, UPGRADE_FOLDER)
			upgrade_edited_path = os.path.join(upgrade_folder_path, 'Edited')
			upgrade_raw_path = os.path.join(upgrade_folder_path, 'Raw')

			try:
				dbx.files_create_folder(edited_fav_path)
				# dbx.files_create_folder(edited_top_path)
				dbx.files_create_folder(edited_portrait_path)
				dbx.files_create_folder(edited_all_path)
				dbx.files_create_folder(other_folder_path)
				dbx.files_create_folder(raw_fav_path)
				dbx.files_create_folder(raw_top_path)
				dbx.files_create_folder(raw_all_path)
				dbx.files_create_folder(upgrade_edited_path)
				dbx.files_create_folder(upgrade_raw_path)
			except Exception, e:
				print e
				# raise e
			else:
				# create upgrade folder link
				try:
					upgrade_link = dbx.sharing_create_shared_link(upgrade_edited_path)
				except Exception, e:
					print e
				else:
					self.upgrade_folder_path = upgrade_link.url


	# create email folder in PHOTO for photographer when people sign up
	# name format, the photo picked by student should be added _fav in filename before the format extension. eg.. DSC_194.jpg -> DSC_194_fav.jpg
	def create_dropbox_photo_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		email = self.email
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		shoot_pk = ts.shoot.pk
		shoot = get_object_or_404(Nextshoot, pk=shoot_pk)
		shoot_name = shoot.name

		root_folder = settings.DROPBOX_PHOTO

		# upload path
		upload_folder_path = os.path.join(root_folder, shoot_name, email)

		# create the folder
		try:
			dbx.files_create_folder(upload_folder_path)
		except Exception, e:
			print e
			return 0
		else:
			return 1


	def retrieve_image(self, **kwargs):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		folder_path = self.dropbox_folder

		path = ''
		if kwargs.get('deliverable_original', None):
			path = os.path.join(folder_path, 'Deliverables')
		elif kwargs.get('deliverable_thumb', None):
			path = os.path.join(folder_path, 'Deliverables_Thumbnail')
		elif kwargs.get('wa_thumb', None):
			path = os.path.join(folder_path, 'Watermarked_Thumbnail')
		elif kwargs.get('wa_original', None):
			path = os.path.join(folder_path, 'Watermarked_Original')

		# original deliverable
		# if kwargs.get('deliverable_original', None):
		try:
			items = dbx.files_list_folder(path).entries
		except Exception, e:
			pass
		else:

			# return a list of image srcs
			urls = []
			for item in items:
				sharing_link = dbx.sharing_create_shared_link(item.path_lower)
				url = str(sharing_link.url)
				url = url[:-4]
				url += 'raw=1'
				urls.append(url)

			return urls

		# no path given return none
		return None


	# check dropbox to see if there are deliverables in the folder in order to check if this person shows up at the shoot
	# could be changed
	def update_showup(self, *args, **kwargs):	
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
	
		db_path = os.path.join(self.dropbox_folder, 'Raw', 'All')

		print 'checking ' + db_path + '...',

		if dbx.files_list_folder(db_path).entries:
			self.show_up = True
			super(Booking, self).save(*args, **kwargs)
			print 'positive'
			return True
		print 'negtive'
		return False


	# go through dropbox to create image instance in the local database
	def create_image(self, raw=False, edited=False, fav=False, top=False, portrait=False, all=False):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		folder_path = self.dropbox_folder

		EDITED_FOLDER = 'Edited'
		OTHER_FOLDER = 'Other'
		RAW_FOLDER = 'Raw'

		# Material Folder
		ALL_PATH = 'All'
		TOP_PATH = 'Top'
		PORTRAIT_PATH = 'Top Portrait'
		FAV_PATH = 'Fav'

		# Upload Folder
		RAW_ALL_WT_path = 'Raw All WT'
		RAW_TOP_WT_PATH = 'Raw Top WT'
		RAW_FAV_WT_PATH = 'Raw Fav WT'
		EDITED_FAV_WT_PATH = 'Edit Fav WT'
		EDITED_FAV_W_PATH = 'Edit Fav W'
		# EDITED_TOP_WT_PATH = 'Edit Top WT'
		# EDITED_TOP_W_PATH = 'Edit Top W'
		EDITED_TOPP_WT_PATH = 'Edit Top Portrait WT'
		EDITED_TOPP_W_PATH = 'Edit Top Portrait W'


		# migrate Raw + All
		if raw:
			if all:
				path = os.path.join(folder_path, OTHER_FOLDER, RAW_ALL_WT_path)

				try:
					items = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][RAW FAV] ' + ' list folder failed'
				else:
					assert len(items) > 0, 'RAW ALL has no items!'
					for item in items:
						sharing_link = dbx.sharing_create_shared_link(item.path_lower)
						url = str(sharing_link.url)
						url = url[:-4]
						url += 'raw=1'

						# create new image instance
						try:
							HeadshotImage.objects.create(
								book=self,
								name=item.name,
								is_raw=True,
								wt_url=url,
								)
						except Exception, e:
							raise e
						else:
							print '[SUCCESS][RAW ALL] ' + item.name

			# migrate Raw + fav (Standard Headshot and free deliverable)
			if fav:
				o_path = os.path.join(folder_path, RAW_FOLDER, FAV_PATH)
				wt_path = os.path.join(folder_path, OTHER_FOLDER, RAW_FAV_WT_PATH)

				try:
					o_items = dbx.files_list_folder(o_path).entries
				except Exception, e:
					print '[FAILED][RAW FAV] ' + ' list folder failed'
				else:
					assert len(o_items) == 1, 'Raw Fav has more than 1 item!'

					o_item = o_items[0]
					o_sharing_link = dbx.sharing_create_shared_link(o_item.path_lower)
					o_url = str(o_sharing_link.url)
					o_url = o_url[:-4]
					o_url += 'raw=1'	

					wt_items = dbx.files_list_folder(wt_path).entries
					assert len(wt_items) == 1, 'RAW FAV WT has more than 1 item!'

					wt_item = wt_items[0]
					wt_sharing_link = dbx.sharing_create_shared_link(wt_item.path_lower)
					wt_url = str(wt_sharing_link.url)
					wt_url = wt_url[:-4]
					wt_url += 'raw=1'

					try:
						# w_url = wt_url since they all 500 * 500
						HeadshotImage.objects.create(
							book=self,
							name=o_item.name,
							is_raw=True,
							is_fav=True,
							o_url=o_url,
							wt_url=wt_url,
							wo_url=wt_url,
							)
					except Exception, e:
						raise e
					else:
						print '[SUCCESS][RAW FAV] ' + o_item.name


			if top:
				path = os.path.join(folder_path, OTHER_FOLDER, RAW_TOP_WT_PATH)
				try:
					items = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][RAW TOP] ' + ' list folder failed'
				else:
					assert len(items) == 1, 'RAW TOP WT has more than 1 item!'
					item = items[0]
					sharing_link = dbx.sharing_create_shared_link(item.path_lower)
					url = str(sharing_link.url)
					url = url[:-4]
					url += 'raw=1'

					# create new image instance
					try:
						HeadshotImage.objects.create(
							book=self,
							name=item.name,
							is_raw=True,
							is_top=True,
							wt_url=url,
							)
					except Exception, e:
						raise e
					else:
						print '[SUCCESS][RAW TOP] ' + item.name


		# edited photo migration
		if edited:
			if fav:
				o_path = os.path.join(folder_path, EDITED_FOLDER, FAV_PATH)
				wt_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_FAV_WT_PATH)
				wo_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_FAV_W_PATH)

				try:
					o_items = dbx.files_list_folder(o_path).entries
					wt_items = dbx.files_list_folder(wt_path).entries
					wo_items = dbx.files_list_folder(wo_path).entries
				except Exception, e:
					print '[FAILED][EDITED FAV] ' + ' list folder failed'
				else:
					assert len(o_items)==len(wt_items)==len(wo_items)==1, 'EDITED FAV O/WT/WO has more than 1 items or None!'
					o_item = o_items[0]
					wt_item = wt_items[0]
					wo_item = wo_items[0]
					o_sharing_link = dbx.sharing_create_shared_link(o_item.path_lower)
					wt_sharing_link = dbx.sharing_create_shared_link(wt_item.path_lower)
					wo_sharing_link = dbx.sharing_create_shared_link(wo_item.path_lower)

					o_url = str(o_sharing_link.url)
					o_url = o_url[:-4]
					o_url += 'raw=1'	
					wt_url = str(wt_sharing_link.url)
					wt_url = wt_url[:-4]
					wt_url += 'raw=1'
					wo_url = str(wo_sharing_link.url)
					wo_url = wo_url[:-4]
					wo_url += 'raw=1'
					try:
						HeadshotImage.objects.create(
							book=self,
							name=o_item.name,
							is_fav=True,
							o_url=o_url,
							wt_url=wt_url,
							wo_url=wo_url,
							)
					except Exception, e:
						raise e
					else:
						print '[SUCCESS][EDITED FAV] ' + o_item.name

			# if top:
			# 	o_path = os.path.join(folder_path, EDITED_FOLDER, TOP_PATH)
			# 	wt_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_TOP_WT_PATH)
			# 	wo_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_TOP_W_PATH)

			# 	try:
			# 		o_items = dbx.files_list_folder(o_path).entries
			# 		wt_items = dbx.files_list_folder(wt_path).entries
			# 		wo_items = dbx.files_list_folder(wo_path).entries
			# 	except Exception, e:
			# 		print '[FAILED][EDITED TOP] ' + ' list folder failed'
			# 	else:
			# 		assert len(o_items)==len(wt_items)==len(wo_items)==1, 'EDITED TOP O/WT/WO has more than 1 items or None!'
			# 		o_item = o_items[0]
			# 		wt_item = wt_items[0]
			# 		wo_item = wo_items[0]
			# 		o_sharing_link = dbx.sharing_create_shared_link(o_item.path_lower)
			# 		wt_sharing_link = dbx.sharing_create_shared_link(wt_item.path_lower)
			# 		wo_sharing_link = dbx.sharing_create_shared_link(wo_item.path_lower)

			# 		o_url = str(o_sharing_link.url)
			# 		o_url = o_url[:-4]
			# 		o_url += 'raw=1'	
			# 		wt_url = str(wt_sharing_link.url)
			# 		wt_url = wt_url[:-4]
			# 		wt_url += 'raw=1'
			# 		wo_url = str(wo_sharing_link.url)
			# 		wo_url = wo_url[:-4]
			# 		wo_url += 'raw=1'
			# 		try:
			# 			HeadshotImage.objects.create(
			# 				book=self,
			# 				name=o_item.name,
			# 				is_top=True,
			# 				o_url=o_url,
			# 				wt_url=wt_url,
			# 				wo_url=wo_url,
			# 				)
			# 		except Exception, e:
			# 			raise e
			# 		else:
			# 			print '[SUCCESS][EDITED TOP] ' + o_item.name

			if portrait:
				o_path = os.path.join(folder_path, EDITED_FOLDER, PORTRAIT_PATH)
				wt_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_TOPP_WT_PATH)
				wo_path = os.path.join(folder_path, OTHER_FOLDER, EDITED_TOPP_W_PATH)

				try:
					o_items = dbx.files_list_folder(o_path).entries
					wt_items = dbx.files_list_folder(wt_path).entries
					wo_items = dbx.files_list_folder(wo_path).entries
				except Exception, e:
					print '[FAILED][EDITED PORTRAIT] ' + ' list folder failed'
				else:
					assert len(o_items)==len(wt_items)==len(wo_items)==1, 'EDITED PORTRAIT O/WT/WO has more than 1 items or None!'
					o_item = o_items[0]
					wt_item = wt_items[0]
					wo_item = wo_items[0]
					o_sharing_link = dbx.sharing_create_shared_link(o_item.path_lower)
					wt_sharing_link = dbx.sharing_create_shared_link(wt_item.path_lower)
					wo_sharing_link = dbx.sharing_create_shared_link(wo_item.path_lower)

					o_url = str(o_sharing_link.url)
					o_url = o_url[:-4]
					o_url += 'raw=1'	
					wt_url = str(wt_sharing_link.url)
					wt_url = wt_url[:-4]
					wt_url += 'raw=1'
					wo_url = str(wo_sharing_link.url)
					wo_url = wo_url[:-4]
					wo_url += 'raw=1'
					try:
						HeadshotImage.objects.create(
							book=self,
							name=o_item.name,
							is_portrait=True,
							o_url=o_url,
							wt_url=wt_url,
							wo_url=wo_url,
							)
					except Exception, e:
						raise e
					else:
						print '[SUCCESS][EDITED PORTRAIT] ' + o_item.name



class HeadshotImage(models.Model):
	book = models.ForeignKey(Booking)
	name = models.CharField(max_length=50, blank=True, null=True)
	is_raw = models.BooleanField(default=False)
	is_fav = models.BooleanField(default=False)
	is_top = models.BooleanField(default=False)
	is_portrait = models.BooleanField(default=False)
	o_url = models.CharField(max_length=150, blank=True, null=True)
	wt_url = models.CharField(max_length=150, blank=True, null=True)
	wo_url = models.CharField(max_length=150, blank=True, null=True)

	def __unicode__(self):
		return str(self.pk) + ' -- ' + self.name

	def is_extra(self):
		return not(self.is_deliverable or self.is_premium or self.is_fullsize)


	def copy_to_upgrade(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_path = self.book.dropbox_folder
		RAW_FOLDER = 'Raw'
		EDITED_FOLDER = 'Edited'
		UPGRADE_FOLDER = os.path.join('Upgrade', 'Edited')
		UPGRADE_RAW_FOLDER = os.path.join('Upgrade', 'Raw')
		ALL_PATH = 'All'
		FAV_PATH = 'Fav'
		TOP_PATH = 'Top'
		PORTRAIT_PATH = 'Top Portrait'

		upgrade_path = os.path.join(root_path, UPGRADE_FOLDER)
		upgrade_raw_path = os.path.join(root_path, UPGRADE_RAW_FOLDER)
		path = ''

		copied = False

		if self.is_raw:
			# raw fav
			if self.is_fav:
				path = os.path.join(root_path, RAW_FOLDER, FAV_PATH)
				try:
					files = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][RAW FAV] ' + self.name + ' list folder failed'
					# raise e
				else:
					assert len(files)==1, 'RAW FAV does not have 1 item!'
					file = files[0]
					try:
						dbx.files_copy(file.path_lower, os.path.join(upgrade_path, file.name))
					except Exception, e:
						print '[FAILED][RAW FAV] ' + self.name + ' copy file failed'
					else:
						copied = True
						print '[SUCCESS][RAW FAV] ' + self.name + ' copied'
			# raw all
			# [TRICKY] copy the file based on file name, move to upgrade raw folder so admin will know what to touch up
			# file name trick, not sustainable, get rid the 'wt'
			else:
				path = os.path.join(root_path, RAW_FOLDER, ALL_PATH)
				try:
					files = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][RAW ALL] ' + self.name + ' list folder failed'
					# raise e
				else:
					# trick
					file_name, file_ext = os.path.splitext(self.name)
					cleaned_file_name = file_name[:-3] + file_ext
					print cleaned_file_name
					file_list = [f for f in files if f.name.lower() == cleaned_file_name.lower()]
					assert len(file_list)>0, '[FAILED][RAW ALL] ' + self.name + ' file name not found among raw all!'
					file = file_list[0]
					try:
						dbx.files_copy(file.path_lower, os.path.join(upgrade_raw_path, file.name))
					except Exception, e:
						print '[FAILED][RAW ALL] ' + self.name + ' copy file failed'
					else:
						copied = True
						print '[SUCCESS][RAW ALL] ' + self.name + ' copied'


		else:
			if self.is_fav:
				path = os.path.join(root_path, EDITED_FOLDER, FAV_PATH)
				try:
					files = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][EDITED FAV] ' + self.name + ' list folder failed'
					# raise e
				else:
					assert len(files)==1, 'EDITED FAV does not have 1 item!'
					file = files[0]
					try:
						dbx.files_copy(file.path_lower, os.path.join(upgrade_path, file.name))
					except Exception, e:
						print '[FAILED][EDITED FAV] ' + self.name + ' copy file failed'
					else:
						copied = True
						print '[SUCCESS][EDITED FAV] ' + self.name + ' copied'
			if self.is_top:
				path = os.path.join(root_path, EDITED_FOLDER, TOP_PATH)
				try:
					files = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][EDITED TOP] ' + self.name + ' list folder failed'
					# raise e
				else:
					assert len(files)==1, 'EDITED TOP does not have 1 item!'
					file = files[0]
					try:
						dbx.files_copy(file.path_lower, os.path.join(upgrade_path, file.name))
					except Exception, e:
						print '[FAILED][EDITED TOP] ' + self.name + ' copy file failed'
					else:
						copied = True
						print '[SUCCESS][EDITED TOP] ' + self.name + ' copied'
			if self.is_portrait:
				path = os.path.join(root_path, EDITED_FOLDER, PORTRAIT_PATH)
				try:
					files = dbx.files_list_folder(path).entries
				except Exception, e:
					print '[FAILED][EDITED PORTRAIT] ' + self.name + ' list folder failed'
					# raise e
				else:
					assert len(files)==1, 'EDITED PORTRAIT does not have 1 item!'
					file = files[0]
					try:
						dbx.files_copy(file.path_lower, os.path.join(upgrade_path, file.name))
					except Exception, e:
						print '[FAILED][EDITED PORTRAIT] ' + self.name + ' copy file failed'
					else:
						copied = True
						print '[SUCCESS][EDITED PORTRAIT] ' + self.name + ' copied'

		return copied



	# temp method to copy to upgrade folder on dropbox
	# def copy_to_upgrade(self, deliverable=False, fullsize=False, premium=False):
	# 	dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
	# 	path = self.book.dropbox_folder
	# 	upgrade_path = os.path.join(path, 'Upgrade')

	# 	# create share link for upgrade folder
	# 	upgrade_link = dbx.sharing_create_shared_link(upgrade_path)

	# 	if deliverable:
	# 		d_path = os.path.join(path, 'Deliverables')
	# 		files = dbx.files_list_folder(d_path).entries
	# 		if files:
	# 			try:
	# 				file = files[0]

	# 				dbx.files_copy(file.path_lower, os.path.join(upgrade_path, file.name))
	# 			except Exception, e:
	# 				print 'copy [deliverable] failed'
	# 				pass
	# 			else:
	# 				print 'copy [deliverable] successfully'

	# 	if fullsize:
	# 		f_path = os.path.join(path, 'Full Size')
	# 		files = dbx.files_list_folder(f_path).entries

	# 		if files:
	# 			try:
	# 				file = files[0]

	# 				dbx.files_copy(file.path_lower, os.path.join(upgrade_path, 'fs' + str(file.name)))
	# 			except Exception, e:
	# 				print 'copy [full size] failed'
	# 				pass
	# 			else:
	# 				print 'copy [full size] successfully'

	# 	if premium:
	# 		p_path = os.path.join(path, 'Premium')
	# 		files = dbx.files_list_folder(p_path).entries

	# 		if files:
	# 			try:
	# 				file = files[0]

	# 				dbx.files_copy(file.path_lower, os.path.join(upgrade_path, 'p' + str(file.name)))
	# 			except Exception, e:
	# 				print 'copy [premium] failed'
	# 				pass
	# 			else:
	# 				print 'copy [premium] successfully'

	# 	return upgrade_link.url



class ImagePurchase(models.Model):
	image = models.ForeignKey(HeadshotImage)
	email = models.EmailField()

	UPGRADES = (
		('fh', 'Free Headshot'),
		('pu', 'Professional Upgrade'),
		('ph', 'Premium Headshot'),
		('pp', 'Premium Portrait'),
	)

	option = models.CharField(max_length=2, choices=UPGRADES, default='pu')
	value = models.DecimalField(max_digits=5, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	charge_successful = models.BooleanField(default=False)
	is_delivered = models.BooleanField(default=False)
	is_copied = models.BooleanField(default=False)



