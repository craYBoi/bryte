"""takeone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from newsletter import views as newsletter_views
from sms import views as sms_views
from userprofile import views as profile_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', newsletter_views.home, name='home'),
    url(r'^about$', newsletter_views.about, name='about'),
    url(r'^photographer/', include('photographer.urls')),

    # get started page
    url(r'^start$', newsletter_views.get_started, name='get_started'),

    # reserve
    url(r'^reserve/', include('reserve.urls')),

    # packages
    url(r'^packages$', newsletter_views.package, name='packages'),

    # faqs
    url(r'^faq$', newsletter_views.faq, name='faqs'),

    # become a photographer
    url(r'^join$', newsletter_views.become_photographer, name='become_photographer'),

    # select photographer
    url(r'^select$', newsletter_views.select_photographer, name='select_photographer'),

    # pricing
    url(r'^pricing$', newsletter_views.pricing, name='pricing'), 

    # blogs 
    url(r'^blog/', include('blog.urls')),

    # user profile
    url(r'^profile$', profile_views.profile, name='profile'),
    # edit profile
    url(r'^profile/edit', profile_views.edit, name='profile_edit'),


    # registration 
    url(r'^accounts/', include('registration.backends.simple.urls')),

    # legal stuff
    url(r'^legal$', newsletter_views.legal, name='legal'),


    # twilio
    url(r'^sms/$', sms_views.sms, name='sms'),
]


if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
