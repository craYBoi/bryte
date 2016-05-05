from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


from datetime import datetime
from photographer.models import Photographer

import os
import dropbox

# Create your models here.

class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
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
		email_list = [e for elem in self.timeslot_set.all() for e in elem.booking_set.all()]
		
		for e in email_list:
			name = e.name 
			title = 'Your Free Headshot at CareerLAB'
			msg = 'Hi ' + name + ',\n\nThis is a reminder that you have booked a free headshot session tomorrow, Wednesday, May, 3rd at ' + str(e.timeslot) + '.\n\nWe look forward to seeing you at the shoot! Arrive 5 minutes before your scheduled time slot is set to begin. You will have 3 minutes to take your headshot since we are fully booked for tomorrow. If you can\'t make it, please respond to this email letting us know.\n\nBest,\nCareerLAB and the Bryte Photo Team.'
			try:
				send_mail('Your Free Headshot at CareerLAB', msg, 'Bryte Photo and CareerLAB <' + settings.EMAIL_HOST_USER + '>', [e.email], fail_silently=False)
		# send_mail('Test', 'This is the test msg', settings.EMAIL_HOST_USER, email_list, fail_silently=False)
			except Exception, e:
				raise e
			else:
				print '[SENT] ' + e.email


	def send_replacement(self):
		max_volumn = 5
		timeslots = self.timeslot_set.all()
		num_slots_available = max_volumn * len(timeslots) - sum(e.current_volumn for e in timeslots)
		
		num_ppl_to_notify = 10 * num_slots_available
		signups = Signup.objects.order_by('timestamp')
		if len(signups) > num_ppl_to_notify:
			signups = signups[:num_ppl_to_notify]

		for e in signups:
			name = e.name
			email = e.email
			title = 'New headshot sessions available!'
			msg = 'Hi ' + name + ',\n\nGreat news! There are now ' + str(num_slots_available) + ' headshots sessions available! We are shooting this afternoon between 130-330. Book your session here:\n\nwww.brytephoto.com/CareerLAB\n\nBest, \nCareerLAB and the Bryte Photo Team'
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
	shoot = models.ForeignKey(Nextshoot, default=Nextshoot.objects.first().pk)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')
		slot_left = ' ------ ' + str(5 - self.current_volumn) + '/5 slots left'
		time_format += slot_left
		if time_format[0] == '0':
			return time_format[1:]
		return time_format

	def increment(self):
		max_volumn = 5

		# this should not be happening
		if not self.is_available:
			print 'this should not be happening'

		if self.current_volumn < max_volumn and self.is_available:
			self.current_volumn += 1
			if self.current_volumn == max_volumn:
				self.is_available = False
			self.save()

	def reset(self):
		self.is_available = True
		self.current_volumn = 0


class Booking(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	timeslot = models.ForeignKey(Timeslot)

	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)





