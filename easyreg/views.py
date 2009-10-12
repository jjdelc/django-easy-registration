# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, RequestSite
from django.contrib.auth import login as auth_login

from easyreg.forms import EmailSignupForm, EmailAuthenticationForm


def login(request, template_name='easyreg/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """
    On GET
    Displays a regular login form with email and password fields.
    If there's an email via GET autocomplete that on the emailfield

    On Post, perform actual login
    """

    # Coded after auth.views.login, since I can't change the 
    # authentication form :(
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():

            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        email = request.GET.get('email', None)
        if email is not None:
            form = EmailAuthenticationForm(initial={
                'email': email,
            })
        else:
            form = EmailAuthenticationForm()

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    return render_to_response(template_name, {
        'form': form,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))


def register(request, template_name='easyreg/register.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """
    If the user exists send to login page
    else, create account, send an email with password and login
    """
    form = EmailSignupForm()

    if request.method == 'POST':
        redirect_to = request.POST.get(redirect_field_name, '')
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            if form.is_new_user():
                # New user:
                # * Create user
                user = form.create_new_user()
                # * Send mail with new password
                form.notify_new_user()
                # * Log the user in
                auth_login(request, form.logged_user())

                if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)
            else:
                # The user exists, send to login page
                return HttpResponseRedirect('%s?email=%s' % (
                    reverse('auth_login'), form.cleaned_data['email']))

    return render_to_response(template_name, {
        'form': form,
    })


