from __future__ import unicode_literals

from django.db import models

from newsletter.models import Price
from userprofile.models import Profile

class Purchase(models.Model):
	package = models.ForeignKey(Price)
	user = models.ForeignKey(Profile)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.user.name
