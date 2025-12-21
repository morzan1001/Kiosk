"""This file holds the user model."""

from typing import List

from sqlalchemy import Column, Float, Integer, String

from src.database.connection import Base
from src.database.crud_mixin import CRUDMixin


class User(Base, CRUDMixin):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nfcid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    credit = Column(Float, nullable=False)
    email = Column(String, nullable=True)
    mattermost_username = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<User(id={self.nfcid}, name='{self.name}', credit={self.credit}, "
            f"email='{self.email}', mattermost_username='{self.mattermost_username}')>"
        )

    @classmethod
    def get_by_id(cls, session, user_id: int) -> "User":
        return session.query(cls).filter_by(id=user_id).first()

    @classmethod
    def get_by_nfcid(cls, session, nfcid: str) -> "User":
        return session.query(cls).filter_by(nfcid=nfcid).first()

    @classmethod
    def get_count(cls, session) -> int:
        return session.query(cls).count()

    @classmethod
    def get_admins(cls, session) -> List["User"]:
        return session.query(cls).filter_by(type="Admin").all()
