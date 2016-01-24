from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Smser(models.Model):
	number = models.CharField(max_length=20)
	from_city = models.CharField(max_length=20)
	from_state = models.CharField(max_length=20)
	use_service = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	def __unicode__(self):
		return self.number

	