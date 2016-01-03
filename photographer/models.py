from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse



class Photographer(models.Model):
	last_name = models.CharField(max_length=120)
	first_name = models.CharField(max_length=120)
	email = models.EmailField()
	slug = models.SlugField(unique=True, null=True, blank=True)
	short_description = models.CharField(max_length=150)
	description = models.TextField()
	phone = models.CharField(max_length=15)
	profile = models.ImageField(upload_to='profile/', null=True)

	def __unicode__(self):
		return self.first_name + ' ' + self.last_name + ': ' + self.email

	def save(self, *args, **kwargs):
		self.slug = slugify(self.first_name + ' ' + self.last_name)
		super(Photographer, self).save(*args, **kwargs)

	def get_absolute_url(self):
		full_name = self.first_name + ' ' + self.last_name
		full_name_slug = slugify(full_name)
		return reverse("photographer_detail", kwargs={"slug": self.slug})


	# some validation (email + phone) here

def image_upload_to(instance, filename):
	title = instance.author.last_name + '_' + instance.author.first_name
	slug = slugify(title)
	extension = filename.split('.')[-1]
	return "photographer/%s/img.%s" %(slug, extension)


class PhotographerImage(models.Model):
	author = models.ForeignKey(Photographer)
	image = models.ImageField(upload_to=image_upload_to)

	def __unicode__(self):
		return self.author.first_name


