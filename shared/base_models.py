"""
Base model classes for PulseWatch.

Provides abstract base classes with common fields and behaviors.
"""
from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base class that adds timestamp fields to models.

    Automatically tracks creation and modification times.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base class that adds soft delete functionality.

    Records are marked as deleted instead of being removed from the database.
    """

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Flag indicating if the record is soft-deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft-deleted"
    )

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class TimestampedSoftDeleteModel(TimestampedModel, SoftDeleteModel):
    """
    Abstract base class combining timestamped and soft delete functionality.

    Provides both automatic timestamps and soft delete capabilities.
    """

    class Meta:
        abstract = True
