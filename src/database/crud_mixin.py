"""Shared CRUD mixin used by SQLAlchemy models."""

from typing import List, Optional, Type, TypeVar

T = TypeVar("T", bound="CRUDMixin")


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (Create, Read, Update, Delete) operations."""

    def create(self, session, commit=True):
        """Adds this instance to the session and optionally commits."""
        session.add(self)
        if commit:
            session.commit()
        return self

    def update(self, session, commit=True, **kwargs):
        """Updates attributes of this instance and optionally commits."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if commit:
            session.commit()
        return self

    def delete(self, session, commit=True):
        """Deletes this instance from the session and optionally commits."""
        session.delete(self)
        if commit:
            session.commit()

    @classmethod
    def read_all(cls: Type[T], session) -> List[T]:
        """Returns all records of this model."""
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls: Type[T], session, item_id: int) -> Optional[T]:
        """Returns a record by its primary key ID."""
        return session.query(cls).filter(cls.id == item_id).first()
