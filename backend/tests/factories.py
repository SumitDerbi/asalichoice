"""
factory_boy factories for the backend test suite.

Conventions:
- One factory per model. Use ``DjangoModelFactory``.
- Email/usernames must be ``factory.Sequence``-unique so parallel tests don't collide.
- Sensitive fields (passwords) default to ``set_unusable_password()``; opt into a real
  password via ``UserFactory(password="...")`` which routes through ``_post_generation``.
- ``BranchFactory`` is a **stub** until M01 lands the real ``Branch`` model. For now it
  just returns an int id so branch-scoped tests have something to bind against.

Import from ``tests.factories`` (e.g. ``from tests.factories import UserFactory``).
"""

from __future__ import annotations

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Create throwaway users with unique emails."""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user-{n}@example.test")
    name = factory.LazyAttribute(lambda obj: obj.email.split("@")[0].replace("-", " ").title())
    is_active = True
    is_staff = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_unusable_password()
        self.save(update_fields=["password"])


class StaffUserFactory(UserFactory):
    is_staff = True


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


def branch_factory(branch_id: int = 1) -> int:
    """Stand-in for a real Branch factory until M01 ships the model.

    Returns the branch id directly. Tests that need a richer object should
    migrate once ``apps.branches.models.Branch`` exists.
    """

    return branch_id
