"""This file holds the user model."""
from sqlalchemy import Column, Integer, String, Float

from src.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nfcid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
    credit = Column(Float, nullable=False)

    def __repr__(self):
        return (
            f"<User(id={self.nfcid}, name='{self.name}', credit={self.credit})>"
        )

    def create(self, session):
        session.add(self)
        session.commit()

    def update(self, session, nfcid=None, user_type=None, name=None, credit=None):
        if nfcid:
            self.nfcid = nfcid
        if user_type:
            self.user_type = user_type
        if name:
            self.name = name
        if credit:
            self.credit = credit
        session.commit()

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def read_all(cls, session):
        users = session.query(cls).all()
        return [(user.id, user.name, user.credit) for user in users]

    @classmethod
    def get_by_id(cls, session, user_id):
        return session.query(cls).filter_by(id=user_id).first()

    @classmethod
    def get_by_nfcid(cls, session, nfcid):
        return session.query(cls).filter_by(nfcid=nfcid).first()

    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()
    
