"""
URLConf for Django easy registration and authentication

You can include() this URLConf under /accounts/ in your main proj
"""

from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

from easyreg import views

urlpatterns = patterns('',
    url(r'^login/$',
        views.login,
        name='auth_login'),

    url(r'^register/$',
        views.register,
        name='easyreg_register'),

    url(r'^logout/',
        auth_views.logout,
        {'template_name': 'easyreg/logout.html'},
        name='auth_logout'),

    url(r'^profile/$',
        direct_to_template,
        {'template': 'easyreg/profile.html'},
        name='profile'),

    url(r'^password/change/$',
        auth_views.password_change,
        name='auth_password_change'),

    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),

    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),

    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),

    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),

)

