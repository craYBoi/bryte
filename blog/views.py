from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

# Create your views here.

from .models import Blog, Comment
from .forms import CommentForm

class BlogListView(ListView):
	model = Blog

	def get_context_data(self, *args, **kwargs):
		context = super(BlogListView, self).get_context_data(*args, **kwargs)
		context['title_text'] = 'Blog Lists'
		return context


def BlogDetailView(request, slug):
	blog = Blog.objects.get(slug=slug)
	comment_form = CommentForm(request.POST or None)
	if comment_form.is_valid() and request.user.is_authenticated():
		instance = comment_form.save(commit=False)
		instance.blog = blog
		instance.profile = request.user.profile
		instance.save()
		return redirect(blog.get_absolute_url())

	comments = Comment.objects.filter(blog=blog)
	context = {
		'blog': blog,
		'comments': comments,
		'comment_form': comment_form,
		'title_text': blog.title,
	}

	return render(request, 'blog/blog_detail.html', context)