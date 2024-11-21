"""This file holds the transaction model."""
from typing import List
from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey

from src.database.connection import Base

# Define the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, category={self.category}, cost='{self.cost}', item_id='{self.item_id}', user_id='{self.user_id}', date='{self.date}')>"
        )

    def create(self, session):
        session.add(self)
        session.commit()

    @classmethod
    def read_all_for_user(cls, session, user_id: int) -> List['Transaction']:
        return session.query(cls).filter(cls.user_id == user_id).all()