from django.contrib.auth.decorators import user_passes_test

def staff_required(function=None, login_url='staff_login'):
    """
    Decorator for views that checks that the user is a staff member.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.user_type == 'STAFF' or u.user_type == 'ADMIN' or u.is_superuser),
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None, login_url='staff_login'):
    """
    Decorator for views that checks that the user is an admin or superuser.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.user_type == 'ADMIN' or u.is_superuser),
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator