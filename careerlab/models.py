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

import os
import dropbox

# max sessions per time slot
MAX_VOLUMN = 4


class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	notified = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.name + ' ' + self.email


class Nextshoot(models.Model):
	photographer = models.ForeignKey(Photographer, related_name='nextshoot_photographer')
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	class Meta:
		ordering = ('-timestamp',)

	def __unicode__(self):
		return self.location + ' - ' + self.photographer.get_full_name()

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
		name = 'CareerLAB1'
		path = os.path.join(root, folder, name)
		folders = dbx.files_list_folder(path)
		for e in folders.entries:
			email = str(e.name)
			new_path = os.path.join(path, email)
			sharing_link = dbx.sharing_create_shared_link(new_path, short_url=False, pending_upload=None)
			title = 'Your headshot photo is available!'
			msg = 'Hi!\n\nGreat news! Here is your retouched headshot photo!\n\n' + str(sharing_link.url) + '\n\nAlso, please enjoy this Promo Video we created with shots from yesterday afternoon.\n\n' + video_link +'\n\n(Let us know if you don\'t want your photo in the video.)\n\nWe\'re always looking to improve your experience with us. In the next day or two, CareerLAB will be sending out a survey about your headshots and the overall experience. Please do us a favor to fill out the survey. That will help us a lot!\n\nThank you!\nCareerLAB and Bryte Photo Team'
			try:
				send_mail(title, msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [email], fail_silently=False)
			except Exception, e:
				raise e
			else:
				print '[SENT] ' + email



class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)
	shoot = models.ForeignKey(Nextshoot, default=Nextshoot.objects.last().pk)
	active = models.BooleanField(default=False)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')

		# overbook trick
		slot_left = min(MAX_VOLUMN - 1, MAX_VOLUMN - self.current_volumn) 

		slot_left_str = ' ------ ' + str(slot_left) + '/3 slots left'
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

	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)

	# override save to add hashid upon creation
	def save(self, *args, **kwargs):
		self.hash_id = uuid4()
		super(Booking, self).save(*args, **kwargs)

	def cancel_order(self):
		ts_pk = self.timeslot.pk
		ts = get_object_or_404(Timeslot, pk=ts_pk)
		
		# open up 1 slot 
		ts.restore_slot()
		self.delete()

	def generate_cancel_link(self):
		return settings.SITE_URL + reverse('careerlab_cancel_order') + '?order_id=' + str(self.hash_id)

	def tips_link(self):
		return settings.SITE_URL + reverse('careerlab_tips')

	def confirmation_email(self):
		name = self.name
		timeslot = self.timeslot
		email = self.email

		msg_body = "Hi " + str(name) + ",\n\nYou\'re receiving this email to confirm that you have booked a Bryte Photo headshot at " + str(timeslot) + ". The shoot will take place at CareerLAB.\n\nCheck out the Bryte Photo Headshot Tips to prepare for your headshot!\n" + self.tips_link() + "\n\nIf you can no longer make it to your headshot, please cancel here:\n" + self.generate_cancel_link() + "\n\nWe have a long waitlist so please let us know if you cannot make your session!!\n\nThanks, \nCareerLAB and Bryte Photo"

		try:
			send_mail('Bryte Photo Headshot Booking Confirmation', msg_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
		except Exception, e:
			print 'Email not sent'
			pass
		else:
			print '[SENT] ' + str(email)
