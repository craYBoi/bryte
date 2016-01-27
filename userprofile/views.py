from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Profile


@login_required
def profile(request):
	user = request.user
	profile = user.profile
	purchases = profile.purchase_set.all()
	context = {
		'name': user.username,
		'profile': profile,
		'purchases': purchases,
		'title_text': profile.user.username,
	}

	return render(request, 'profile.html', context)
