from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from uuid import uuid4
from datetime import datetime
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


	def get_date_string(self):
		timeslots = self.timeslot_set.filter(active=True)
		if timeslots:
			return str(timeslots.first().time.strftime('%b %-d'))
		return None


	def get_time_interval_string(self):
		timeslots = self.timeslot_set.filter(active=True)
		if timeslots:
			a = sorted(timeslots, reverse=True)
			str_time_start = a[0].time.strftime('%-I:%M %p')
			str_time_end = a[-1].time.strftime('%-I:%M %p')
			return str_time_start + ' - ' + str_time_end
		return None


	def send_reminder(self):
		bookings = [e for elem in self.timeslot_set.filter(active=True) for e in elem.booking_set.all()]
		
		for e in bookings:
			name = e.name 
			title = 'Bryte Photo Headshot tomorrow!'
			msg = 'Hi ' + name + ',\n\nThis email is to remind you about your free Bryte Photo headshot on Friday at ' + str(e.timeslot) + '. The shoot will take place at CareerLAB.\n\nWe look forward to seeing you at the shoot! Please refer to the Bryte Photo Headshot Tips to prepare:\n'+ e.tips_link() +'\n\nIf you can no longer make it to your headshot, please cancel here\n' + e.generate_cancel_link() +'\n\nWe have a long waitlist so please let us know if you cannot make it!!\n\nBest,\nCareerLAB and the Bryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [e.email], fail_silently=False)
		# send_mail('Test', 'This is the test msg', settings.EMAIL_HOST_USER, email_list, fail_silently=False)
			except Exception, e:
				raise e
			else:
				print '[SENT] ' + e.email


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
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		video_link = 'https://www.dropbox.com/sh/8kmxk6kvwefvkld/AADpuwmJbcjYLWE3q6TewUDha?dl=0'
		root = '/'
		folder = 'Deliverable'
		name = 'CareerLAB2'
		path = os.path.join(root, folder, name)
		folders = dbx.files_list_folder(path)
		count_sent = 0
		count_not_sent = 0
		for e in folders.entries:
			email = str(e.name)
			new_path = os.path.join(path, email)
			sharing_link = dbx.sharing_create_shared_link(new_path, short_url=False, pending_upload=None)
			title = 'Your Touched up Bryte Photo Headshot'
			msg = 'Hi!\n\nYour touched up Bryte Photo headshot is available!\n\n' + str(sharing_link.url) + '\n\n We\'re always looking to improve your experience. Email us what you think of your photo. We greatly appreciate your feedback!\n\nAlso, we occasionally put our headshots on our website or Facebook Page. Let us know if you do not want your photo to be displayed.\n\nBest,\nBryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				print '[NOT SENT] ' + email
				count_not_sent += 1
			else:
				print '[SENT] ' + email
				count_sent += 1
		print str(count_sent) + ' emails sent'
		print str(count_not_sent) + ' email NOT SENT'



class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	notified = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	shoot = models.ForeignKey(Nextshoot, default=Nextshoot.objects.first().pk)

	def __unicode__(self):
		return self.name + ' ' + self.email



class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)
	shoot = models.ForeignKey(Nextshoot)
	active = models.BooleanField(default=False)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p') + ' ' + self.shoot.location

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
		message.set_subject('Bryte Photo Headshot Booking Confirmation') 
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
		except SendGridClientError, e:
			raise e
		except SendGridServerError, e:
			raise e



	def create_dropbox_folder(self):
		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		email = self.email
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		shoot_pk = ts.shoot.pk
		shoot = get_object_or_404(Nextshoot, pk=shoot_pk)
		# shoot_name = shoot.name

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
