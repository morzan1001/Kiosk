"""This file holds the transaction model."""

from typing import List

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from src.database.connection import Base
from src.database.crud_mixin import CRUDMixin


class Transaction(Base, CRUDMixin):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, category={self.category}, cost='{self.cost}', "
            f"item_id='{self.item_id}', user_id='{self.user_id}', date='{self.date}')>"
        )

    @classmethod
    def read_all_for_user(cls, session, user_id: int) -> List["Transaction"]:
        return session.query(cls).filter(cls.user_id == user_id).all()
