from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """Decorator ให้เฉพาะ User ในกลุ่ม 'admin' เข้าได้"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.groups.filter(name="admin").exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
