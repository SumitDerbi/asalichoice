"""Tests for :class:`apps.core.models.SoftDeleteModel`.

We deliberately avoid creating a throwaway concrete model + migration:
the soft-delete behaviour is fully exercisable by mocking
:meth:`django.db.models.Model.save` and asserting on field state. The
audit-log model + integration tests verify that abstract mixins compose
correctly with a real table.
"""

from __future__ import annotations

from unittest.mock import patch

from django.db import models

from apps.core.models import ActiveOnlyManager, BaseModel, SoftDeleteModel, TimeStampedModel


class _Thing(SoftDeleteModel):
    """Concrete-shaped subclass used only for unit assertions (never saved)."""

    name = models.CharField(max_length=10)

    class Meta:
        # ``app_label`` is required because the test module is not part of
        # an installed app; ``managed=False`` prevents Django from trying
        # to create a table for it.
        app_label = "tests_softdelete"
        managed = False


def test_default_field_values():
    thing = _Thing()
    assert thing.is_active is True
    assert thing.deleted_at is None


def test_delete_soft_deletes_and_calls_save_with_minimal_fields():
    thing = _Thing()
    with patch.object(models.Model, "save") as mock_save:
        result = thing.delete()
    assert thing.is_active is False
    assert thing.deleted_at is not None
    mock_save.assert_called_once()
    _, kwargs = mock_save.call_args
    assert kwargs["update_fields"] == ["is_active", "deleted_at"]
    # delete() returns a (count, by_label) tuple compatible with QuerySet.delete().
    count, labels = result
    assert count == 1
    assert labels[_Thing._meta.label] == 1


def test_restore_reactivates_row():
    thing = _Thing(is_active=False)
    from django.utils import timezone

    thing.deleted_at = timezone.now()
    with patch.object(models.Model, "save"):
        thing.restore()
    assert thing.is_active is True
    assert thing.deleted_at is None


def test_hard_delete_calls_super_delete():
    thing = _Thing()
    with patch.object(models.Model, "delete") as mock_delete:
        thing.hard_delete()
    mock_delete.assert_called_once()


def test_default_manager_filters_inactive():
    """ActiveOnlyManager attaches a filter on ``is_active=True``."""

    mgr = ActiveOnlyManager()
    mgr.model = _Thing
    with patch.object(models.Manager, "get_queryset") as mock_qs:
        mock_qs.return_value.filter.return_value = "filtered"
        result = mgr.get_queryset()
    mock_qs.return_value.filter.assert_called_once_with(is_active=True)
    assert result == "filtered"


def test_base_model_composes_all_three_mixins():
    assert issubclass(BaseModel, SoftDeleteModel)
    assert issubclass(BaseModel, TimeStampedModel)
    # AuditableModel composition is checked by field presence.
    assert "created_by" in {f.name for f in BaseModel._meta.get_fields()}
    assert "updated_by" in {f.name for f in BaseModel._meta.get_fields()}
    assert "created_at" in {f.name for f in BaseModel._meta.get_fields()}
    assert "updated_at" in {f.name for f in BaseModel._meta.get_fields()}
    assert "is_active" in {f.name for f in BaseModel._meta.get_fields()}
    assert "deleted_at" in {f.name for f in BaseModel._meta.get_fields()}
    assert BaseModel._meta.abstract is True
