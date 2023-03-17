from django.http import HttpResponseRedirect
from django.urls import reverse, resolve


class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        current_url = resolve(request.path_info).url_name

        response = self.get_response(request)
        if not request.user.is_authenticated and current_url != 'login': # in Django > 3 this is a boolean
            return HttpResponseRedirect(reverse('login'))
        
        # Code to be executed for each request/response after
        # the view is called.

        return response