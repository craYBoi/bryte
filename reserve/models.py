from __future__ import unicode_literals

from django.db import models

from photographer.models import Photographer
from userprofile.models import Profile
from newsletter.models import Price


# Create your models here.
class Reservation(models.Model):
	photographer = models.ForeignKey(Photographer)
	profile = models.ForeignKey(Profile, blank=True, null=True)
	first_name = models.CharField(max_length=100, blank=True, null=True)
	last_name = models.CharField(max_length=100, blank=True, null=True)
	price = models.ForeignKey(Price)
	phone = models.CharField(max_length=15)
	email = models.EmailField(blank=True, null=True)
	note = models.TextField(blank=True, null=True)
	date_range = models.CharField(max_length=150)
	business_name = models.CharField(max_length=100)
	datetime = models.DateTimeField(blank=True, null=True)
	is_complete = models.BooleanField(default=False)
	is_paid = models.BooleanField(default=False)
	is_taken = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	dropbox_link = models.CharField(max_length=150, blank=True, null=True)


	def __unicode__(self):
		return self.photographer.get_full_name()

	def status(self):
		if self.is_paid:
			return 'Paid'
		elif self.is_complete:
			return 'Complete'
		elif self.is_taken:
			return 'Taken'
		else:
			return 'Pending'

	def creative_status(self):
		if self.is_paid:
			return 'Complete'
		if self.is_complete:
			return 'Waiting for client to pay'
		if self.is_taken:
			return 'Project in progress'
		return 'Pending'

	def creative_status_code(self):
		# 1 pending
		# 2 taken
		# 3 complete
		# 4 paid

		if self.is_paid:
			return 4
		if self.is_complete:
			return 3
		if self.is_taken:
			return 2
		return 1

	def creative_pending(self):
		return not self.is_complete and not self.is_paid and not self.is_taken