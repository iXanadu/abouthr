"""
Context Processors for Multi-Tenant Django Applications

Copy this to accounts/context_processors.py in your project.
Add to TEMPLATES['OPTIONS']['context_processors'] in settings.py:
    'accounts.context_processors.user_context',

These context processors make user and account information
available in all templates without explicitly passing them.
"""

from accounts.models import Account


def user_context(request):
    """
    Add user-related context to all templates.

    Returns:
        dict: Context variables available in all templates:
            - is_account_owner: Boolean, whether user owns an account
            - home_url: URL name for user's home/dashboard page
            - user_profile: The user's profile object (if authenticated)
            - account: The user's account (if authenticated)
    """
    context = {
        'is_account_owner': False,
        'home_url': 'accounts:login',  # Default for unauthenticated
    }

    if request.user.is_authenticated:
        # Check if user owns an account
        is_owner = Account.objects.filter(owner=request.user).exists()
        context['is_account_owner'] = is_owner

        # Get user profile
        profile = getattr(request.user, 'profile', None)
        if profile:
            context['user_profile'] = profile
            context['account'] = profile.account

            # Determine home URL based on role
            # Customize this logic for your application's dashboard structure
            if is_owner or profile.system_role == 'account_owner':
                context['home_url'] = 'accounts:owner_dashboard'
            elif profile.is_admin:
                context['home_url'] = 'accounts:admin_dashboard'
            else:
                context['home_url'] = 'accounts:user_dashboard'

    return context
