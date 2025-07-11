from django.shortcuts import redirect
from functools import wraps

def redirect_authenticated_user(to='profile'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(to)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

