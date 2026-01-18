"""
Core Base Models for Multi-Tenant Django Applications

Copy this to core/models.py in your project.
These abstract base models provide consistent patterns for:
- Timestamps (created_at, updated_at)
- Multi-tenant account scoping
- User tracking for audit trails

Usage:
    from core.models import BaseModel, AccountScopedModel, UserTrackingModel

    class MyModel(AccountScopedModel):
        # Your model fields here
        name = models.CharField(max_length=255)
        # account field is inherited from AccountScopedModel
"""

from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """
    Abstract base model with common timestamp fields for all models.

    Provides:
        - created_at: Auto-set when record is created
        - updated_at: Auto-updated when record is modified
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AccountScopedModel(BaseModel):
    """
    Abstract base model for multi-tenant models that belong to an account.

    Use this for any model that needs to be isolated per account/tenant.
    The related_name pattern '%(app_label)s_%(class)s_set' ensures
    unique reverse relation names across apps.

    Example:
        class Client(AccountScopedModel):
            name = models.CharField(max_length=255)
            # account field is inherited
    """
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )

    class Meta:
        abstract = True


class UserTrackingModel(AccountScopedModel):
    """
    Abstract base model that tracks which user created/modified the record.

    Extends AccountScopedModel with user tracking for audit trails.
    Use SET_NULL to preserve records if users are deleted.

    Example:
        class Document(UserTrackingModel):
            title = models.CharField(max_length=255)
            # account, created_by, modified_by fields are inherited
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_created'
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_modified'
    )

    class Meta:
        abstract = True
