from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def api_login_required(view_func):
    """
    Custom decorator that checks if user is authenticated via API tokens
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has valid API tokens in session
        if (request.session.get('is_authenticated') and 
            request.session.get('access_token') and 
            request.session.get('user_client_id')):
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to login page if not authenticated
            return redirect('login')
    return _wrapped_view 