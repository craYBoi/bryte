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
import dropbox
import sendgrid
from sendgrid import SendGridError, SendGridClientError, SendGridServerError


# call sendgrid api
sg = sendgrid.SendGridClient(settings.SENDGRID_KEY, None, raise_errors=True)


# max sessions per time slot
MAX_VOLUMN = 4


class Nextshoot(models.Model):
	photographer = models.ForeignKey(Photographer, related_name='nextshoot_photographer')
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	name = models.CharField(max_length=100, blank=True, null=True)
	school = models.CharField(max_length=60, default='not assigned')

	class Meta:
		ordering = ('-timestamp',)


	# override save method to first create folder
	def save(self, *args, **kwargs):
		name = self.location + ' - ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

		# populate the shoot name field
		self.name = name

		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		root_folder = settings.DROPBOX_PATH

		folder_path = os.path.join(root_folder, name)

		try:
			dbx.files_create_folder(folder_path)
		except Exception, e:
			raise e
			pass

		super(Nextshoot, self).save(*args, **kwargs)


	def __unicode__(self):
		return self.location + ' - ' + self.photographer.get_full_name()


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


	def send_reminder(self):
		bookings = [e for elem in self.timeslot_set.filter(active=True) for e in elem.booking_set.all()]
		
		count = 0
		for booking in bookings:
			if(booking.reminder_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


	def close_shoot(self):
		timeslots = self.timeslot_set.filter(active=True)
		for timeslot in timeslots:
			timeslot.active = False
			timeslot.save()


	def send_replacement(self):
		timeslots = self.timeslot_set.filter(active=True)
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
			msg = 'Hi ' + name + ',\n\nGreat news! There are now ' + str(num_slots_available) + ' headshots sessions available! We are shooting tomorrow afternoon between 12:30 pm - 3:30 pm on the first floor of Brown CareerLAB. Book your session here:\n\nwww.brytephoto.com/CareerLAB\n\nBest, \nCareerLAB and the Bryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
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


	def send_dropbox_links(self):
		bookings = [e for elem in self.timeslot_set.filter(active=True) for e in elem.booking_set.all()]
		
		count = 0
		for booking in bookings:
			if(booking.delivery_email()):
				count += 1
		print 'Total --- ' + str(len(bookings)) + ' Emails\nSENT --- ' + str(count) + ' Emails'


class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	notified = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	shoot = models.ForeignKey(Nextshoot, blank=True, null=True)

	def __unicode__(self):
		return self.name + ' ' + self.email



class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)
	shoot = models.ForeignKey(Nextshoot)
	active = models.BooleanField(default=False)

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


	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)

	# override save to add hashid upon creation
	def save(self, *args, **kwargs):
		# increment the timeslot
		self.timeslot.increment()

		N = 6
		self.hash_id = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

		self.create_dropbox_folder()
		super(Booking, self).save(*args, **kwargs)

	def cancel_order(self):
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		
		# open up 1 slot 
		ts.restore_slot()

		# add delete the corresponding dropbox
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)
		try:
			deleted_folder = dbx.files_delete(self.dropbox_folder)
		except Exception, e:
			print e
			pass

		self.delete()

	def generate_cancel_link(self):
		return settings.SITE_URL + reverse('careerlab_cancel_order') + '?order_id=' + str(self.hash_id)

	def tips_link(self):
		return settings.SITE_URL + reverse('careerlab_tips')

	def confirmation_email(self):
		name = self.name
		first_name = name.split(' ')[0]
		timeslot = self.timeslot
		location = timeslot.shoot.location
		email = self.email

		# msg_body = "Hi " + str(name) + ",\n\nYou\'re receiving this email to confirm that you have booked a Bryte Photo headshot at " + str(timeslot) + ". The shoot will take place at CareerLAB.\n\nCheck out the Bryte Photo Headshot Tips to prepare for your headshot!\n" + self.tips_link() + "\n\nIf you can no longer make it to your headshot, please cancel here:\n" + self.generate_cancel_link() + "\n\nWe have a long waitlist so please let us know if you cannot make your session!!\n\nThanks, \nCareerLAB and Bryte Photo"

		# try:
		# 	send_mail('Bryte Photo Headshot Booking Confirmation', msg_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
		# except Exception, e:
		# 	print 'Email not sent'
		# 	pass
		# else:
		# 	print '[SENT] ' + str(email)

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Your headshot booking confirmation') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id','71ff210a-f5f5-4c3a-876a-81d46197ed77')
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-timeslot-', str(timeslot))
		message.add_substitution('-location-', location)
		message.add_substitution('-cancel_link-', self.generate_cancel_link())

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			print '[SENT] --- ' + str(email)


	def reminder_email(self):
		sent = False
		name = self.name
		first_name = name.split(' ')[0]
		timeslot = self.timeslot
		location = timeslot.shoot.location
		email = self.email

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Tips for your headshot tomorrow') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id','ef27b980-d764-4ee3-8ffc-e8cd7f9377d8')
		message.add_substitution('-first_name-', first_name)
		message.add_substitution('-time_slot-', str(timeslot))
		message.add_substitution('-location-', location)
		message.add_substitution('-cancel_link-', self.generate_cancel_link())

		try:
			sg.send(message)
		except Exception, e:
			print '[NOT SENT] --- ' + str(email) 
		else:
			send = True
			print '[SENT] --- ' + str(email)
		return send


	def delivery_email(self):
		sent = False
		name = self.name
		first_name = name.split(' ')[0]
		email = self.email
		hash_id = self.hash_id

		message = sendgrid.Mail()
		message.add_to(email)
		message.set_from('Bryte Photo Inc <' + settings.EMAIL_HOST_USER + '>')
		message.set_subject('Download your free Linkedin headshot') 
		message.set_html('Body')
		message.set_text('Body')
		message.add_filter('templates','enable','1')
		message.add_filter('templates','template_id','d2750257-04b4-4e24-a785-aa34a7942606')
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

		# create the folder
		try:
			dbx.files_create_folder(upload_folder_path)
		except Exception, e:
			print e
			pass
		else:
			# store the upload path in the Booking
			self.dropbox_folder = upload_folder_path

			# create the All and Deliverables subfolder
			all_path = os.path.join(upload_folder_path, 'All')
			deliverable_path = os.path.join(upload_folder_path, 'Deliverables')
			try:
				dbx.files_create_folder(all_path)
				dbx.files_create_folder(deliverable_path)
			except Exception, e:
				print e
				pass


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


	# go through dropbox to create image instance in the local database
	def create_image(self):
		dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
		folder_path = self.dropbox_folder

		deliverable_o_path = os.path.join(folder_path, 'Deliverables')
		deliverable_t_path = os.path.join(folder_path, 'Deliverables_Thumbnail')
		watermarked_t_path = os.path.join(folder_path, 'Watermarked_Thumbnail')
		watermarked_o_path = path = os.path.join(folder_path, 'Watermarked_Original')

		# Deliverable Original 
		try:
			deliverable_o_list = dbx.files_list_folder(deliverable_o_path).entries
			deliverable_t_list = dbx.files_list_folder(deliverable_t_path).entries

			# see if they share the same length
			assert(len(deliverable_o_list) == len(deliverable_t_list)), 'Original - Thumbnails don\t have same number of files'

		except Exception, e:
			print 'access deliverable original folder fail'
			pass
		else:
			if deliverable_t_list:
				for deliverable_t, deliverable_o in zip(deliverable_t_list, deliverable_o_list):
					print 'Creating Deliverable Original..'
					url = dbx.sharing_create_shared_link(deliverable_o.path_lower)
					t_url = dbx.sharing_create_shared_link(deliverable_t.path_lower)
					url = str(url.url)
					url = url[:-4]
					url += 'raw=1'
					t_url = str(t_url.url)
					t_url = t_url[:-4]
					t_url += 'raw=1'
					try:
						HeadshotImage.objects.create(
							book=self,
							is_watermarked=False,
							is_deliverable=True,
							original_url=url,
							thumbnail_url=t_url,
							)
					except Exception, e:
						print 'create image instance fail'
						raise e
					else:
						print 'image [deliverable] successfully created'


		# Watermark Original
		try:
			watermarked_o_list = dbx.files_list_folder(watermarked_o_path).entries
			watermarked_t_list = dbx.files_list_folder(watermarked_t_path).entries
		except Exception, e:
			print 'access watermark folder fail'
			pass
		else:
			if watermarked_t_list:
				for watermarked_t, watermarked_o in zip(watermarked_t_list, watermarked_o_list):
					print 'Creating Watermarked Original..'
					url = dbx.sharing_create_shared_link(watermarked_o.path_lower)
					t_url = dbx.sharing_create_shared_link(watermarked_t.path_lower)
					url = str(url.url)
					url = url[:-4]
					url += 'raw=1'
					t_url = str(t_url.url)
					t_url = t_url[:-4]
					t_url += 'raw=1'
					try:
						HeadshotImage.objects.create(
							book=self,
							is_watermarked=True,
							is_deliverable=False,
							original_url=url,
							thumbnail_url=t_url,
							)
					except Exception, e:
						print 'create image instance fail'
						raise e
					else:
						print 'image [watermark original] successfully created'


class HeadshotImage(models.Model):
	book = models.ForeignKey(Booking)
	is_watermarked = models.BooleanField(default=False)
	is_deliverable = models.BooleanField(default=False)
	original_url = models.CharField(max_length=80)
	thumbnail_url = models.CharField(max_length=80)

	def __unicode__(self):
		return str(self.pk) + ' -- ' + self.book.__unicode__()

class ImagePurchase(models.Model):
	image = models.ForeignKey(HeadshotImage)
	email = models.EmailField()

	UPGRADES = (
		('oh', 'Original Headshot'),
		('st', 'Standard Touchup'),
		('pt', 'Premium Touchup'),
		('pp', 'Passport Package'),
	)

	option = models.CharField(max_length=2, choices=UPGRADES, default='og')
	address = models.CharField(max_length=100, blank=True, null=True)
	request = models.TextField(blank=True, null=True)
	value = models.DecimalField(max_digits=5, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	charge_successful = models.BooleanField(default=True)



