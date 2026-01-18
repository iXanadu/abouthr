"""
Account and UserProfile Models for Multi-Tenant Django Applications

Copy these to accounts/models.py in your project.
These models provide the foundation for multi-tenant SaaS applications.

Key Concepts:
    - Account: The tenant/organization entity
    - UserProfile: Extended user information linked to an Account
    - System roles vs Functional roles for flexible permissions
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from core.models import BaseModel


class Account(BaseModel):
    """
    Organization/Team entity - represents a tenant in the system.

    This is the core multi-tenancy model. All business data should be
    scoped to an Account to ensure proper data isolation.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly name"
    )

    # Account status
    is_active = models.BooleanField(default=True)

    # Owner of the account (super admin for this account)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_accounts',
        null=True,
        blank=True
    )

    # Branding
    logo = models.ImageField(
        upload_to='account_logos/',
        null=True,
        blank=True
    )
    primary_color = models.CharField(
        max_length=7,
        default='#000000',
        help_text="Hex color for branding"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AccountSettings(BaseModel):
    """
    Configuration and preferences for an account.

    Use this for account-level settings that shouldn't clutter
    the main Account model. One-to-one relationship ensures
    each account has exactly one settings record.
    """
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='settings'
    )

    # Feature Flags - enable/disable features per account
    enable_feature_x = models.BooleanField(default=True)
    enable_feature_y = models.BooleanField(default=True)

    # Notification Settings
    notification_email = models.EmailField(
        blank=True,
        help_text="Default email for system notifications"
    )

    class Meta:
        verbose_name_plural = "Account settings"

    def __str__(self):
        return f"{self.account.name} Settings"


class UserProfile(BaseModel):
    """
    Extended user information and account membership.

    Links Django's User model to an Account for multi-tenancy.
    Implements a two-tier permission system:
        1. System Role: Controls system-level access (admin, user, etc.)
        2. Functional Roles: Boolean flags for feature access

    This allows users to have multiple functional capabilities
    (e.g., is_agent AND is_coordinator) while having a single system role.
    """

    # System role choices - hierarchical permissions
    SYSTEM_ROLE_CHOICES = [
        ('account_owner', 'Account Owner'),
        ('admin', 'Administrator'),
        ('user_manager', 'User Manager'),
        ('user', 'User'),
    ]

    # User status choices
    USER_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('onboarding', 'Onboarding'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='user_profiles'
    )

    # System Role - controls system-level access
    system_role = models.CharField(
        max_length=50,
        choices=SYSTEM_ROLE_CHOICES,
        default='user',
        help_text="System-level role controlling access permissions"
    )

    # Functional Roles - boolean flags for feature access
    # Customize these for your application's needs
    is_admin = models.BooleanField(
        default=False,
        help_text="Has administrative access to account features"
    )

    # Example functional roles - customize for your domain:
    # is_agent = models.BooleanField(default=False)
    # is_coordinator = models.BooleanField(default=False)
    # is_operations = models.BooleanField(default=False)

    # Status
    status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default='active'
    )

    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title or position"
    )

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.account.name}"

    @property
    def is_account_owner(self):
        """Check if this user is the owner of their account."""
        return self.account.owner == self.user

    @property
    def can_manage_users(self):
        """Check if this user can manage other users."""
        return self.system_role in ['account_owner', 'admin', 'user_manager']
