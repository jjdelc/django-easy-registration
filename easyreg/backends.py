# -*- coding: utf-8 -*-
"""
Common authentication backends
"""

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    """
    Authenticates against django.contrib.auth.models.User's email field.
    """
    def authenticate(self, email=None, password=None):
        """
           Authenticate using an email parameter instead of the default django
           username.
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

def authenticate(email=None, password=None):
    """
    Authenticates the user based on the email field 
    and sets the backend information
    """
    try:
        backend = EmailBackend()
        user = backend.authenticate(email=email, password=password)
    except TypeError:
        # This backend doesn't accept these credentials 
        # as arguments. Try the next one.
        return None
    # Annotate the user object with the path of the backend.
    if user:
        user.backend = "%s.%s" % (
            backend.__module__, 
            backend.__class__.__name__
        )
    return user
