from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
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
import csv
import StringIO

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
FIRST_AFTER_SHOOT_EMAIL_ID = '4463c390-4085-4936-863d-12652c8a0a0d'
SURVEY_EMAIL_TO_FREE_CLIENT_ID = '6e9cb0a1-535b-42dc-9279-4b9d23f19a1a'
SURVEY_EMAIL_TO_FAVORED_CLIENT_ID = '5c562a0c-25f6-4151-a81a-99089ea00d61'
FORGET_TO_ORDER_YOUR_HEADSHOT_ID = '6f6a328f-11b2-48c9-8879-751fe4c8b268'


# max sessions per time slot
MAX_VOLUMN = 8


class Nextshoot(models.Model):
	photographer = models.ForeignKey(Photographer, related_name='nextshoot_photographer')
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	name = models.CharField(max_length=100, blank=True, null=True)
	school = models.CharField(max_length=60, default='not assigned')
	date = models.DateField(default=timezone.now)
	active = models.BooleanField(default=True)
	max_volumn = models.PositiveSmallIntegerField(default=4)
	is_serving = models.BooleanField(default=True)
	basic_price = models.PositiveSmallIntegerField(default=8)
	professional_price = models.PositiveSmallIntegerField(default=11)
	customized_price = models.PositiveSmallIntegerField(default=15)

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
		# self.create_touchup_folder()


	def __unicode__(self):
		return self.name


	def update_cust_types(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]

		total = len(bookings)
		no_show = 0
		no_download = 0
		free = 0
		paid = 0

		for booking in bookings:
			cust_type = booking.update_cust_type()
			if cust_type == 1:
				no_download += 1
			elif cust_type == 2:
				free += 1
			elif cust_type == 3:
				paid += 1
			else:
				no_show += 1

		print 'Total number: ' + str(total)
		print 'Paid customer: ' + str(paid)
		print 'Free customer: ' + str(free)
		print 'No download customer: ' + str(no_download)
		print 'No show customer: ' + str(no_show)


	def create_time_slot(self, start, end):
		delta = timedelta(minutes=10)
		while start<end:
			# create the timeslot
			Timeslot.objects.create(
				time=start,
				shoot=self,
				)

			print start,
			print ' created'
			start+=delta

		print 'Down..'


	def create_folder_after_close(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]

		print 'creating folders...'
		count = 0
		for booking in bookings:
			# create dropbox in PROD and PHOTO
			if(booking.create_dropbox_folder() and booking.create_dropbox_photo_folder()):
				count += 1
				print str(booking.email) + ' [DONE]'

		print '\n'
		print str(len(bookings)) + ' bookings in total'
		print str(count) + ' bookings dropbox folder created'


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


	def migrate_locals(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]

		print 'Migrating to locals...'
		count = 0
		for b in bookings:
			if(b.migrate_local()):
				count += 1
				print str(b.email) + ' [DONE]'

		print '\n'
		print str(len(bookings)) + ' to be migrated in total'
		print str(count) + ' migrated'


	# photo to touchup 
	def photo_to_touchups(self, folder_name):

		print 'Moving photos from PHOTO to TOUCHUP..'
		# iterate though showups
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		for b in bookings:

			b.photo_to_touchup(folder_name)

		print '\nDONE!'



	def deliver_deliverables(self):
		print 'Delivering the photos..'

		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		for b in bookings:
			b.deliver_deliverable()

		print '\nDONE!'



	# discard noshows
	def discard_noshows(self):
		print 'discarding noshows...'

		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=False)]

		for b in bookings:
			b.delete()

		print 'discarded.'



	# close the cycle
	def close_cycle(self):
		self.is_serving = False
		super(Nextshoot, self).save()


	def notify_signups_all(self):
		pass


	# garbage after here


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
						# print 'Fav not found in folder'
						pass
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


	# CHECK TOUCHUP Folder
	def touchup_folder_check(self):
		booking_emails = [e.email for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]
		num_of_showups = len(booking_emails)

		num_of_email_in_booking_failure = 0
		num_of_file_ext_failure = 0

		# store the photo name for checking edited folder
		# photo_name -> num of edits (should be 3, pr, pt, s)
		photo_names = {}

		# check both total number and name format of the picture
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		root_folder = settings.DROPBOX_TOUCHUP
		folder_path = os.path.join(root_folder, self.name)

		try:
			items = dbx.files_list_folder(folder_path).entries
		except Exception, e:
			print e
			return 0
		else:
			for item in items:
				# check if that's a folder or a file
				if isinstance(item, dropbox.files.FileMetadata):
					# if it's a file, first check name format
					name = item.name

					# populate the dict for checking the edited folder later
					photo_names[name.lower()] = 0

					email, file_name = name.split('+')
					# check if email is in the booking list
					try:
						assert email in booking_emails
					except Exception, e:
						print '[FAIL] Email name is not in the Booking list -- ' + str(email)
						num_of_email_in_booking_failure += 1

					# check if it ends with jpg
					ext = os.path.splitext(file_name)[-1]
					try:
						assert ext.lower() == '.jpg'
					except Exception, e:
						print '[FAIL] file does not end with jpg -- ' + str(email)
						num_of_file_ext_failure += 1


			# check the total number of files match the number of showups
			num_of_pic = len([item for item in items if isinstance(item, dropbox.files.FileMetadata)])
			try:
				assert num_of_pic == num_of_showups
			except Exception, e:
				print '[FAIL] Total number does not match ---\nNum of showups: ' + str(num_of_showups) + '\nNum of files: ' + str(num_of_pic) 
			else:
				print '[SUCCESS] Total number matches!'


			print '\nTotal Cases: ' + str(num_of_showups)
			print 'Failure email name in booking: ' + str(num_of_email_in_booking_failure)
			print 'Failure file ext: ' + str(num_of_file_ext_failure)


		# check edited folder script
		print '\nChecking Edited Folder...'

		edited_path = os.path.join(folder_path, 'Edited')
		try:
			items = dbx.files_list_folder(edited_path).entries
		except Exception, e:
			print e
			return 0
		else:
			# check to see if the name appears 3 times for _pr, _pt, _s
			names = [item.name.replace('_pf', '').replace('_pt', '').replace('_s', '') for item in items]
			for name in names:
				if name.lower() in photo_names:
					photo_names[name.lower()] += 1

			for key, val in photo_names.iteritems():
				try:
					assert val == 3
				except Exception, e:
					print '[FAIL] don\'t have 3 copies, have ' + str(val) + ' instead -- ' + str(key)
				else:
					print '[SUCCESS] 3 copies confirmed -- ' + str(key)	



	# PHOTO check script
	def photo_folder_check(self):
		# iterate through photos, if none meaning no show
		# if any, check if there's 1 _fav
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_folder = settings.DROPBOX_PHOTO
		folder_path = os.path.join(root_folder, self.name)

		try:
			items = dbx.files_list_folder(folder_path).entries
		except Exception, e:
			print e
			return 0
		else:
			for item in items:
				booking_path = item.path_lower
				try:
					booking_photos = dbx.files_list_folder(booking_path).entries
				except Exception, e:
					raise e
				else:
					if not len(booking_photos) == 0:
						# check only 1 fav
						booking_photos_names = [b.name for b in booking_photos]
						count = 0
						for booking_photo_name in booking_photos_names:
							if '_fav' in booking_photo_name.lower():
								count += 1
						try:
							assert count == 1
						except Exception, e:
							print '[FAILURE] number of fav not equal to 1 --- ' + item.name
						else:
							print '[SUCCESS] num of fav is 1 --- ' + item.name



	# compress the image in TOUCH Edited

	# migrate image from TOUCH Edited to PROD/TEST Edited 
	def migrate_touchup_to_prod(self):
		# different from photo to prod, since all the photos from 1 shoot is in the same folder, no need to call Booking subclass
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_folder = settings.DROPBOX_TOUCHUP
		folder_path = os.path.join(root_folder, self.name, 'Edited')

		EDITED_FOLDER = 'Edited'
		RAW_FOLDER = 'Raw'
		FAV_PATH = 'Fav'
		TOP_PATH = 'Top'
		PORTRAIT_PATH = 'Top Portrait'

		# migrate one by one
		try:
			items = dbx.files_list_folder(folder_path).entries
		except Exception, e:
			raise e
		else:
			all_photo = [(item.name, item.path_lower) for item in items]

			for photo in all_photo:
				# extract email address and photo type, locate the dest folder
				name = photo[0]
				email = name.split('+')[0]
				file_name = name.split('+')[1]
				ext = os.path.splitext(file_name)[0].split('_')[-1]
				dest_folder = ''
				photo_type = ''

				# need to find the Booking instance and access the dropbox_folder
				try:
					b = Booking.objects.filter(email=email).order_by('-pk')[0]
				except Exception, e:
					print '[FAILURE] Can\'t find the corresponding booking instance --- ' + email
				else:
					# target dest folder
					if ext == 's':
						dest_folder = os.path.join(b.dropbox_folder, RAW_FOLDER, FAV_PATH, file_name)
						photo_type = 'RAW FAV'
					elif ext == 'pf':
						dest_folder = os.path.join(b.dropbox_folder, EDITED_FOLDER, FAV_PATH, file_name)
						photo_type = 'EDITED FAV'
					elif ext == 'pt':
						dest_folder = os.path.join(b.dropbox_folder, EDITED_FOLDER, PORTRAIT_PATH, file_name)
						photo_type = 'EDITED PORTRAIT'

					# actual migration
					try:
						dbx.files_copy(photo[1], dest_folder)
					except Exception, e:
						print 'It seems ' + photo_type + ' has already been migrated..  --- ' + name
					else:
						print '[SUCCESS] ' + photo_type + ' migrated from TOUCHUP --- ' + email



	# migrate raw image from PHOTO to PROD/TEST RAW
	def migrate_photo_to_prod(self):
		# need to call sub migrate method under Booking, do the same thing as update showup
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		count = 0
		for booking in bookings:
			if(booking.migrate_photo_to_prod_single()):
				count += 1

		print '\n'
		print str(len(bookings)) + ' bookings in total to be migrated to Raw'
		print str(count) + ' bookings migrated to Raw'


	def send_reminder(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]
		
		count = 0
		for booking in bookings:
			if(booking.db_reminder_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	# need to disable signup and cancel
	def close_shoot(self):
		self.active = False
		super(Nextshoot, self).save()


	def send_replacement(self):
		timeslots = self.timeslot_set.all()
		num_slots_available = self.max_volumn * len(timeslots) - sum(e.current_volumn for e in timeslots)

		num_ppl_to_notify = 8 * num_slots_available
		signups = Signup.objects.filter(shoot=self).filter(notified=False).filter(cancelled=False).order_by('timestamp')

		if len(signups) > num_ppl_to_notify:
			signups = signups[:num_ppl_to_notify]

		datetime = self.get_date_string() + ', ' + self.get_time_interval_string()
		location = self.school + ' ' + self.location

		if self.school == 'Brown University':
			url = 'www.brytephoto.com/school/brown'
		elif self.school == 'Rhode Island College':
			url = 'www.brytephoto.com/school/ric'
		elif self.school == 'Boston University':
			url = 'www.brytephoto.com/school/bu'
		else:
			url = ''

		count = 0
		for e in signups:
			count += 1
			name = e.name
			email = e.email
			title = 'New headshot sessions are opened. Sign up now!'
			msg = 'Hi ' + name + ',\n\nGreat news! There are now ' + str(num_slots_available) + ' headshots sessions available! We are shooting on' + datetime + ', at ' + location + '. Book your session here:\n\n' + url + '\n\nBest, \nTeam Bryte'
			try:
				send_mail(title, msg, 'Bryte <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				raise e
			else:
				e.notified = True
				e.save()
				print '[SENT] ' + email
		print str(count) + ' emails sent'


	# temp method integrated with dropbox
	def send_delivery(self):
		# filter out the no shows
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]
		
		count = 0
		for booking in bookings:
			if(booking.my_headshot_1_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def first_followups_after_shoot(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		count = 0
		for booking in bookings:
			if(booking.first_after_shoot_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def survey_emails_to_free_client(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		count = 0
		for booking in bookings:
			if(booking.survey_email_to_free_client()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def survey_emails_to_favored_client(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		count = 0
		for booking in bookings:
			if(booking.survey_email_to_favored_client()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def forget_to_order_your_headshot_emails(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		count = 0
		for booking in bookings:
			if(booking.forget_to_order_your_headshot_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	# temp method integrated with dropbox
	def update_showups(self):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]

		count = 0
		for booking in bookings:
			if(booking.update_showup()):
				count += 1

		print '\n'
		print str(len(bookings)) + ' people in total'
		print str(count) + ' people showed up!'


	def create_images(self, raw=False, edited=False, fav=False, top=False, portrait=False, all=False):
		bookings = [e for elem in self.timeslot_set.all() for e in elem.booking_set.filter(show_up=True)]

		for booking in bookings:
			# this already handles the empty folder
			booking.create_image(raw=raw, edited=edited, fav=fav, top=top, portrait=portrait, all=all)


class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	notified = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	shoot = models.ForeignKey(Nextshoot, blank=True, null=True)
	# see if it's from cancelling the booking order
	cancelled = models.BooleanField(default=False)


	def __unicode__(self):
		return self.name + ' ' + self.email


	def notify_signup(self):
		first_name = self.name.split(' ')[0]
		email = self.email
		school = self.shoot.school
		shoot = Nextshoot.objects.filter(school=school).order_by('-date')[0]
		datetime = shoot.get_date_string() + ', ' + shoot.get_time_interval_string()
		location = school + ' ' + shoot.location
		url = ''

		if school == 'Brown University':
			url = 'www.brytephoto.com/school/brown'
		elif school == 'Boston University':
			url = 'www.brytephoto.com/school/bu'
		elif school == 'Brown GradCON':
			url = 'www.brytephoto.com/school/GradCON'
		elif self.school == 'Rhode Island College':
			url = 'www.brytephoto.com/school/ric'

		title = 'New headshot sessions are opened. Sign up now!'
		msg = 'Hi ' + first_name + ',\n\nGreat news! There are new headshots sessions available! We are shooting on ' + datetime + ', at ' + location + '. Book your session here:\n\n' + url + '\n\nBest, \nTeam Bryte'
		try:
			send_mail(title, msg, 'Bryte <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
		except Exception, e:
			raise e
		else:
			print '[SENT] ' + email
			return 1



class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)
	shoot = models.ForeignKey(Nextshoot)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p') + ' ' + str(self.shoot.location)

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')

		# overbook trick
		slot_left = min(MAX_VOLUMN - 1, MAX_VOLUMN - self.current_volumn) 

		slot_left_str = ' ------ ' + str(slot_left) + '/3 headshot sessions left'
		# time_format += slot_left_str
		if time_format[0] == '0':
			return time_format[1:]
		return time_format


	def date_and_time(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def increment(self):
		# this should not be happening
		if not self.is_available:
			print 'this should not be happening'

		if self.current_volumn < self.shoot.max_volumn and self.is_available:
			self.current_volumn += 1
			if self.current_volumn == self.shoot.max_volumn:
				self.is_available = False
			self.save()

	def reset(self):
		self.is_available = True
		self.current_volumn = 0

	def restore_slot(self):
		self.is_available = True
		self.current_volumn -= 1
		self.save()



# 1 day before the shoot
# manually create the dropbox folders
# create booking folder in PROD
# self.create_dropbox_folder()
# create booking folder in PHOTO
# self.create_dropbox_photo_folder()	



class Booking(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	timeslot = models.ForeignKey(Timeslot)
	hash_id = models.CharField(max_length=50, default='default')
	dropbox_folder = models.CharField(max_length=100, blank=True, null=True)
	upgrade_folder_path = models.CharField(max_length=100, blank=True, null=True)
	show_up = models.BooleanField(default=False)

	TYPE = (
		(1, 'No free nor buy'),
		(2, 'Free only'),
		(3, 'Paid customer'),
		)

	cust_type = models.PositiveSmallIntegerField(choices=TYPE, blank=True, null=True)


	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)


	# override save to add hashid upon creation
	# make sure can't book for new slots once the shoot is closed, but it's already in the logic, so it's good right now
	def save(self, *args, **kwargs):
		# increment the timeslot
		self.timeslot.increment()

		N = 6
		self.hash_id = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

		super(Booking, self).save(*args, **kwargs)


	def update_cust_type(self):
		# update the cust type
		# filter showup first, then according to Order
		if self.show_up:

			orders = HeadshotOrder.objects.filter(booking=self)
			if orders:
				for order in orders:
					if order.total > 0:
						# paid customer
						self.cust_type = 3
						break

					else:
						# free customer
						self.cust_type = 2
			else:
				self.cust_type = 1

		else:
			print '[NO SHOW] -- ' + self.email
			return 0
				

		if self.cust_type == 1:
			print '[NO TYPE] -- ' + self.email
		elif self.cust_type == 2:
			print '[FREE TYPE] -- ' + self.email
		elif self.cust_type == 3:
			print '[PAID TYPE] -- ' + self.email
			

		super(Booking, self).save()
		return self.cust_type



	def cancel_order(self):
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		
		# open up 1 slot 
		ts.restore_slot()

		self.delete()

		# add to signup list
		try:
			s = Signup.objects.create(
				email = self.email,
				name = self.name,
				timestamp = self.timestamp,
				cancelled = True,
				shoot = self.timeslot.shoot,
				)
		except Exception, e:
			print e
			pass
		else:
			print 'Signup instance is created ' + str(self.email)

	# migrate from photo folder to touchup folder according to HeadshotPurchase data
	def photo_to_touchup(self, folder_name):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		photo_folder_path = os.path.join(settings.DROPBOX_PHOTO)
		touchup_folder_path = os.path.join(settings.DROPBOX_TOUCHUP, folder_name)

		email = self.email

		orders = self.headshotorder_set.all()

		shoot_name = self.timeslot.shoot.name

		photo_path = os.path.join(photo_folder_path, shoot_name, email)

		if orders:
			for order in orders:
				# print 'order!!\n\n\n\n'
				purchases = order.headshotpurchase_set.filter(copied_to_touchup=False)
				# or could just filter order instances


				if purchases:

					copied_flag = True
					for purchase in purchases:
						# copy photo to touchup
						image_name = purchase.image.name
						p_id = purchase.id


						# free or upgraded folder
						if purchase.touchup == 1:
							touchup_dest_path = os.path.join(touchup_folder_path, 'Free', str(p_id)+image_name)
							touchup_text = 'Free'
						else:
							touchup_dest_path = os.path.join(touchup_folder_path, 'Upgraded', str(p_id)+image_name)
							touchup_text = 'Paid'


						# rewrite the copy part
						photo_instance_path = os.path.join(photo_path, image_name)
						# print photo_instance_path
						# print touchup_folder_path
						# print '\n\n'


						try:
							dbx.files_copy(photo_instance_path, touchup_dest_path)
						except Exception, e:
							print '[FAILED] copy from photo to touchup: ' + image_name + ' ' + touchup_text
							# print e
						else:
							print '[SUCCESS] copy from photo to touchup: ' + image_name + ' ' + touchup_text
							# update the flag

						purchase.copied_to_touchup = True
						super(HeadshotPurchase, purchase).save()

				else:
					# print 'Seems all the photos are copied to touchup already: ' + str(email)
					pass
				# assign touchup folder to the order

				if not order.touchup_folder:
					order.touchup_folder = folder_name
					super(HeadshotOrder, order).save()

							# for item in items:
							# 	if image_name.lower() == item.name.lower():
							# 		# copy from photo to touchup
							# 		print 'copying to touchup folder.. ' + item.name + str(email)

							# 		try:
							# 			dbx.files_copy(item.path_lower, touchup_folder_path)
							# 		except Exception, e:
							# 			print 'copy from photo to touchup failed, maybe it\'s already there'
							# 			# raise e
							# 			pass
							# 		else:
							# 			print 'copy from photo to touchup successful'
							# 			# change the flag of purchase and order
							# 			purchase.copied_to_touchup = True
							# 			super(HeadshotPurchase, purchase).save()


  # iterate through every booking instance,
  # decide whether to send deliverable or not
	def deliver_deliverable(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		time_now = timezone.now()

		orders = self.headshotorder_set.filter(copied_to_prod=True).filter(delivered=False)

		# see if need to send out
		# could be used to implement the expedite delivery

		# TODO make sure the orders are seperated by at least 1 day

		# ASSUMING orders are not placed in the same day, otherwise it's gonna send more than 1 delivery emails
		for order in orders:

			print 'processing order..' + str(order.booking.email)

			# expedite or regular shipping
			# shipping_days = 4
			# if order.express_shipping:
			# 	shipping_days = 2

			# delta = timedelta(days=shipping_days)

			# # if it's been processed more than 5 days
			# if order.timestamp + delta < time_now:

				# send delivery email
			self.photo_delivery_email()

			# change the flag
			order.delivered = True
			super(HeadshotOrder, order).save()

			# change the flags of its purchases
			for p in order.headshotpurchase_set.all():
				p.delivered = True
				super(HeadshotPurchase, p).save()

			print 'order delivered!\n' + str(order.booking.email)
			# else:
			# 	print 'order don\'t need to be delivered yet. ' + str(order.timestamp) + ' ' + str(order.booking.email)



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
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
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
		elif school == 'Rhode Island College':
			school_url = 'ric'
		elif school == 'Brown University':
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
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Tips for your upcoming LinkedIn photoshoot') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', DB_REMINDER_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-time_slot-', str(timeslot.date_and_time()))
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

		my_headshot_link = settings.SITE_URL + '/headshot/?id=' + hash_id + '&utm_source=My%20Headshot%20My%Headshot&utm_medium=Campaign%20Medium%20URL%20Builder'

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')

		# ccri followup
		# message.set_subject('We\'ve fixed the issue, and now you can use mobile to download your free headshot')
		message.set_subject('The photos you took')
 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')

		message.add_filter('templates','template_id', MY_HEADSHOT_1_ID)


		message.set_categories(category)

		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-unique_id-', hash_id)
		message.add_substitution('-my_headshot-', my_headshot_link)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def first_after_shoot_email(self):
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
			email_template = json.loads(sgapi.client.templates._(FIRST_AFTER_SHOOT_EMAIL_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')

		# ccri followup
		# message.set_subject('We\'ve fixed the issue, and now you can use mobile to download your free headshot')
		message.set_subject('A guide to after your photoshoot')
 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')

		message.add_filter('templates','template_id', FIRST_AFTER_SHOOT_EMAIL_ID)

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
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
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

		my_headshot_link = settings.SITE_URL + '/headshot/?id=' + hash_id + '&utm_source=Photo%20Delivery%20My%20Headshot&utm_medium=Campaign%20Medium%20URL%20Builder'

		one_star_link = settings.SITE_URL + '/school/feedback?id=' + hash_id + '&rating=1'
		two_star_link = settings.SITE_URL + '/school/feedback?id=' + hash_id + '&rating=2'
		three_star_link = settings.SITE_URL + '/school/feedback?id=' + hash_id + '&rating=3'
		four_star_link = settings.SITE_URL + '/school/feedback?id=' + hash_id + '&rating=4'
		five_star_link = settings.SITE_URL + '/school/feedback?id=' + hash_id + '&rating=5'

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Your purchase is ready for download!') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', PHOTO_DELIVERY_ID)
		message.set_categories(category)
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-download_link-', self.upgrade_folder_path)
		message.add_substitution('-my_headshot-', my_headshot_link)

		message.add_substitution('-one_star-', one_star_link)
		message.add_substitution('-two_star-', two_star_link)
		message.add_substitution('-three_star-', three_star_link)
		message.add_substitution('-four_star-', four_star_link)
		message.add_substitution('-five_star-', five_star_link)


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
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
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

	def forget_to_order_your_headshot_email(self):
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
			email_template = json.loads(sgapi.client.templates._(FORGET_TO_ORDER_YOUR_HEADSHOT_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		my_headshot_link = settings.SITE_URL + '/headshot/?id=' + hash_id + '&utm_source=My%20Headshot%20My%Headshot&utm_medium=Campaign%20Medium%20URL%20Builder'

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')

		# ccri followup
		# message.set_subject('We\'ve fixed the issue, and now you can use mobile to download your free headshot')
		message.set_subject('Forget to order your Linkedin photo?')
 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')

		message.add_filter('templates','template_id', FORGET_TO_ORDER_YOUR_HEADSHOT_ID)


		message.set_categories(category)

		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-unique_id-', hash_id)
		message.add_substitution('-my_headshot-', my_headshot_link)

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send

	def survey_email_to_free_client(self):
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
			email_template = json.loads(sgapi.client.templates._(SURVEY_EMAIL_TO_FREE_CLIENT_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('a free coffee for your feedback') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', SURVEY_EMAIL_TO_FREE_CLIENT_ID)
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


	def survey_email_to_favored_client(self):
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
			email_template = json.loads(sgapi.client.templates._(SURVEY_EMAIL_TO_FAVORED_CLIENT_ID).get().response_body)
			versions = email_template.get('versions')
			version_number = [v.get('name') for v in versions if v.get('active')][0]
			email_purpose = email_template.get('name')
		except Exception, e:
			pass

		category = [school + ' - ' + str(date), email_purpose, version_number]

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('a free coffee for your feedback') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id', SURVEY_EMAIL_TO_FAVORED_CLIENT_ID)
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
			TBT_FOLDER = 'To Be retouched'
			DELIVERABLE_FOLDER = 'Deliverable'
			RAW_FOLDER = 'Raw'

			tbt_path = os.path.join(upload_folder_path, TBT_FOLDER)
			deliverable_path = os.path.join(upload_folder_path, DELIVERABLE_FOLDER)
			raw_path = os.path.join(upload_folder_path, RAW_FOLDER)

			try:
				dbx.files_create_folder(tbt_path)
				dbx.files_create_folder(deliverable_path)
				dbx.files_create_folder(raw_path)
			except Exception, e:
				print e
				print self.email
				return False
				# raise e
			else:
				# create upgrade folder link
				try:
					deliverable_link = dbx.sharing_create_shared_link(deliverable_path)
				except Exception, e:
					print e
					return False
					
				else:
					self.upgrade_folder_path = deliverable_link.url
					super(Booking, self).save()
					return True


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
			print self.email
			return False
		else:
			return True



	# check dropbox to see if there are deliverables in the folder in order to check if this person shows up at the shoot
	# could be changed
	# [TODO] change to check PHOTO folder
	def update_showup(self, *args, **kwargs):	
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_folder = settings.DROPBOX_PHOTO
		folder_path = os.path.join(root_folder, self.timeslot.shoot.name, self.email)

		try:
			items = dbx.files_list_folder(folder_path).entries
		except Exception, e:
			print e
			print self.email
			return 0
		else:
			if not len(items) == 0:
				# meaning this person shows up
				self.show_up = True
				super(Booking, self).save(*args, **kwargs)
				print '[Positive] -- ' + self.email
				return True
			print '[Negative] -- ' + self.email
			return False


	# compress PHOTO folder for raw
	# download, run compression, upload
	def compress_photo_folder_single(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_folder = settings.DROPBOX_PHOTO
		folder_path = os.path.join(root_folder, self.timeslot.shoot.name, self.email)


		# compress all of them
		# download the file
		print 'Downloading from folder ' + folder_path + '...'

		# store the file names for clean up
		file_names = []

		try:
			items = dbx.files_list_folder(path).entries
		except Exception, e:
			print 'Folder don\'t exist, skip..'
			return None
		else:
			if items:
				for item in items:
					try:
						f = dbx.files_download_to_file(os.path.join(os.getcwd(), item.name), item.path_lower)
					except Exception, e:
						print '[FAILURE] Downloading fail... --- ' + f.name
					else:
						file_names.append(f.name)
						print '[SUCCESS] Downloaded --- ' + f.name

			print file_names




	def migrate_photo_to_prod_single(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_folder = settings.DROPBOX_PHOTO
		folder_path = os.path.join(root_folder, self.timeslot.shoot.name, self.email)
		
		try:
			items = dbx.files_list_folder(folder_path).entries
		except Exception, e:
			print e
			return 0
		else:
			# find favorite and migrate to RAW FAV
			# others go to RAW ALL
			success_all = False
			success_fav = False

			fav_photo = 0

			all_photo = [(item.name, item.path_lower) for item in items]
			for name, path in all_photo:
				if '_fav' in name.lower():
					# by removing fav from all, the rest go to RAW ALL
					fav_photo = (name, path)
					all_photo.remove(fav_photo)


			# Now do the migration to PROD
			RAW_FOLDER = 'Raw'
			FAV_PATH = 'Fav'
			ALL_PATH = 'All'
			TOP_PATH = 'TOP'

			fav_dest_folder = os.path.join(self.dropbox_folder, RAW_FOLDER, TOP_PATH)
			all_dest_folder = os.path.join(self.dropbox_folder, RAW_FOLDER, ALL_PATH)


			# fav migration
			print 'Migrating fav photo to raw top... ' + str(self.email)
			try:
				# remove _fav for fav photo
				dbx.files_copy(fav_photo[1], os.path.join(fav_dest_folder, fav_photo[0].replace('_fav', '')))
			except Exception, e:
				print 'It seems RAW TOP has already been migrated..  --- ' + str(self.email) + '\n'
				# return 0
			else:
				print '[SUCCESS] RAW TOP migrated from PHOTO --- ' + str(self.email) + '\n'
				success_fav = True


			# all migration
			print 'Migrating all photo to raw all... ' + str(self.email)
			try:
				for photo in all_photo:
					dbx.files_copy(photo[1], os.path.join(all_dest_folder, photo[0]))
			except Exception, e:
				print 'It seems RAW ALL has already been migrated.. --- ' + str(self.email) + '\n'
				# return 0
			else:
				print '[SUCCESS] RAW ALL migrated from PHOTO --- ' + str(self.email) + '\n'
				success_all = True

			return success_all and success_fav



	# NEW migrate to local image instance
	def migrate_local(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		folder_path = self.dropbox_folder

		raw_path = os.path.join(folder_path, 'Raw')

		try:
			items = dbx.files_list_folder(raw_path).entries
		except Exception, e:
			raise e
		else:			
			for item in items:
				sharing_link = dbx.sharing_create_shared_link(item.path_lower)
				url = str(sharing_link.url)
				url = url[:-4]
				url += 'raw=1'

				# create new image instance
				try:

					OriginalHeadshot.objects.create(
					booking=self,
					name=item.name,
					raw_url=url,
					)
				except Exception, e:
					raise e
					return False
				else:
					print '[SUCCESS] create local instance ' + item.name
		return True


class OriginalHeadshot(models.Model):
	booking = models.ForeignKey(Booking)
	name = models.CharField(max_length=50)
	raw_url = models.CharField(max_length=80, blank=True, null=True)
	deliverable_url = models.CharField(max_length=80, blank=True, null=True)
	hash_id = models.CharField(max_length=20, default='default')


	def __unicode__(self):
		return str(self.booking.email) + ' ' + self.name

	def save(self, *args, **kwargs):
		N = 16
		self.hash_id = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

		super(OriginalHeadshot, self).save(*args, **kwargs)



class HeadshotOrder(models.Model):
	booking = models.ForeignKey(Booking)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	total = models.DecimalField(max_digits=5, decimal_places=2)
	address = models.CharField(max_length=100, blank=True, null=True)
	copied_to_touchup = models.BooleanField(default=False)
	copied_to_prod = models.BooleanField(default=False)
	delivered = models.BooleanField(default=False)
	touchup_folder = models.CharField(max_length=30, blank=True, null=True)
	express_shipping = models.BooleanField(default=False)
	feedback_rating = models.PositiveSmallIntegerField(blank=True, null=True)


	def __unicode__(self):
		return str(self.booking.email) + ' ' + str(self.timestamp) + ' ' + str(self.total)



class HeadshotPurchase(models.Model):
	image = models.ForeignKey(OriginalHeadshot)
	raw_url = models.CharField(max_length=80, blank=True, null=True)

	order = models.ForeignKey(HeadshotOrder, blank=True, null=True)

	charged = models.BooleanField(default=False)
	copied = models.BooleanField(default=False)

	TOUCHUPS = (
		(1, 'Free'),
		(2, 'Basic'),
		(3, 'Standard'),
		(4, 'Customized'),
		)

	touchup = models.PositiveSmallIntegerField(choices=TOUCHUPS, default=1)
	special_request = models.CharField(max_length=200, blank=True, null=True)

	BACKGROUNDS = (
		(1, 'White'),
		(2, 'Polished Gray'),
		(3, 'Designer Bricks'),
		(4, 'Sanguine Blue'),
		(5, 'Nighttime Black'),
		(6, 'Light Cream'),
		(7, 'Frosty Blue'),
		(8, 'Riverside Blue'),
		(9, 'Airy Gray'),
		(10, 'Vibrant Orange'),
		(11, '31st Story Office'),
		(12, 'Eclectic Bookcase'),
		(13, 'Firm Hallway'),
		(14, 'Urban Walkway'),
		)

	background = models.PositiveSmallIntegerField(choices=BACKGROUNDS, default=1)

	PACKAGES = (
		(1, 'No Package'),
		(2, 'Wallet Prints'),
		(3, 'Friends and Family'),
		(4, 'Complete Collection'),
		(5, 'Premium Framed Print'),
		)
	package = models.PositiveSmallIntegerField(choices=PACKAGES, default=1)
	total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	# keep track of if customer finishes a round
	complete = models.BooleanField(default=False)
	hash_id = models.CharField(max_length=8)
	copied_to_touchup = models.BooleanField(default=False)
	copied_to_prod = models.BooleanField(default=False)
	delivered = models.BooleanField(default=False)

	def __unicode__(self):
		return self.image.name + ', touchup: ' + str(self.get_touchup_display()) + ', bg: ' + str(self.get_background_display()) + ', total: ' + str(self.total)


	def save(self, *args, **kwargs):
		self.raw_url = self.image.raw_url
		super(HeadshotPurchase, self).save()


	def copy_to_tbr(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		root_path = self.image.booking.dropbox_folder
		RAW_FOLDER = 'Raw'
		TBR_FOLDER = 'To Be retouched'

		raw_path = os.path.join(root_path, RAW_FOLDER, self.image.name)
		tbr_path = os.path.join(root_path, TBR_FOLDER, self.image.name)

		try:
			dbx.files_copy(raw_path, tbr_path)
		except Exception, e:
			print 'Not copied'
		else:
			# update the copied field
			self.copied = True
			super(HeadshotPurchase, self).save()
			print 'Successfully Copied'



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



