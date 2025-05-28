# data_pro/context_processors.py
def user_type(request):
    """Adds user type information to template context"""
    if request.user.is_authenticated:
        return {
            'is_superadmin': request.user.user_type == 'SUPERADMIN',
            'is_client_admin': request.user.user_type == 'CLIENT_ADMIN',
        }
    return {
        'is_superadmin': False,
        'is_client_admin': False,
    }