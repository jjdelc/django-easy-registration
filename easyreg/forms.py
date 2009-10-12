# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site, RequestSite
from django.template.loader import render_to_string

try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail


class EmailSignupForm(forms.Form):
    email = forms.EmailField()

    def is_new_user(self):
        """
        Returns a boolean value determining if the given email is for
        a new user or an existing one
        """
        self.email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=self.email)
            setattr(self, 'user', user)
            return False
        except User.DoesNotExist:
            return True

    def make_random_password(self):
        """
        Sets a new random password to set to the user
        It stores it on self.password for future use
        """
        password = User.objects.make_random_password()
        setattr(self, 'password', password)

    def create_new_user(self):
        """
        Creates a new user for the entered password.
        The user's username will be a slugification of the email
        (beware for dups?)
        """
        user = User(username=slugify(self.email),
            email=self.email)
        self.make_random_password()
        user.set_password(self.password)
        user.save()
        setattr(self, 'user', user)
        return user
        
    def logged_user(self):
        logged_user = authenticate(email=self.email, password=self.password)
        setattr(self, 'logged_user', logged_user)
        return self.logged_user

    def notify_new_user(self):
        """
        Sends a welcome mail to the newly created user
        """
        current_site = Site.objects.get_current()
        mail_body = render_to_string(
            'easyreg/mail/success_registration.txt', {
                'email': self.email,
                'password': self.password,
                'site': current_site,
            })
        mail_subject = render_to_string(
            'easyreg/mail/success_registration_subject.txt', {
                'site': current_site,
            })
        send_mail(mail_subject, mail_body, settings.DEFAULT_FROM_EMAIL,
            [self.email])

        self.user.message_set.create(message=_(u'We just created an account for you, check your mail for more information.'))


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request=None, *args, **kwargs):
        """
        Coded after auth.forms.AuthenticationForm
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_(u'Please enter a correct email address and password. Note that both are case sensitive'))
        
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_(u'Your Web Browser doesnt\' appear tu have cookies enabled. Cookies are required for logging in.'))
            
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None
