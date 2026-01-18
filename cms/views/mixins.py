"""
CMS Access Mixins

Provides authentication and authorization for CMS views.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class CMSAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires user to be logged in and have CMS access.

    CMS access is granted if user:
    - Is a superuser, OR
    - Has is_admin=True on their UserProfile, OR
    - Has system_role in ['account_owner', 'admin']
    """
    login_url = '/accounts/login/'

    def test_func(self):
        user = self.request.user

        # Superusers always have access
        if user.is_superuser:
            return True

        # Check UserProfile permissions
        try:
            profile = user.profile
            if profile.is_admin:
                return True
            if profile.system_role in ['account_owner', 'admin']:
                return True
        except AttributeError:
            pass

        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(self.request, "You don't have permission to access the CMS.")
        return redirect('/')
