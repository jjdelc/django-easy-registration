from django.views.generic.simple import direct_to_template
from easyreg.forms import EmailSignupForm

def index(request):
    request.session.set_test_cookie()
    return direct_to_template(request, 'index.html', {
        'easyform': EmailSignupForm
    })
    
