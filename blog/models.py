from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models
from photographer.models import Photographer
from django.core.urlresolvers import reverse

# Create your models here.
class Blog(models.Model):
	photographer = models.ForeignKey(Photographer)
	title = models.CharField(max_length=120)
	content = models.TextField()
	slug = models.SlugField(unique=True, null=True, blank=True)

	def __unicode__(self):
		return self.title

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Blog, self).save(*args, **kwargs)

	def get_absolute_url(self):
		title = slugify(self.title)
		return reverse("blog_detail", kwargs={"slug": self.slug})
