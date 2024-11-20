"""This file holds the user model."""
from typing import List
from sqlalchemy import Column, Integer, String, Float

from src.database.connection import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nfcid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    credit = Column(Float, nullable=False)
    email = Column(String, nullable=True)
    mattermost_username = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<User(id={self.nfcid}, name='{self.name}', credit={self.credit}, email='{self.email}', mattermost_username='{self.mattermost_username}')>"
        )

    def create(self, session):
        session.add(self)
        session.commit()

    def update(self, session, nfcid=None, type=None, name=None, credit=None, email=None, mattermost_username=None):
        if nfcid:
            self.nfcid = nfcid
        if type:
            self.type = type
        if name:
            self.name = name
        if credit is not None:
            self.credit = credit
        if email is not None:
            self.email = email
        if mattermost_username is not None:
            self.mattermost_username = mattermost_username
        session.commit()

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def read_all(cls, session) -> List['User']:
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, session, user_id: int) -> 'User':
        return session.query(cls).filter_by(id=user_id).first()

    @classmethod
    def get_by_nfcid(cls, session, nfcid: str) -> 'User':
        return session.query(cls).filter_by(nfcid=nfcid).first()

    @classmethod
    def get_count(cls, session) -> int:
        return session.query(cls).count()
    
    @classmethod
    def get_admins(cls, session) -> List['User']:
        return session.query(cls).filter_by(type='Admin').all()