from django.shortcuts import render
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

# Create your views here.

from .models import Blog

class BlogListView(ListView):
	model = Blog


def BlogDetailView(request, slug):
	blog = Blog.objects.get(slug=slug)

	context = {}

	return render(request, 'blog/blog_detail.html', context)