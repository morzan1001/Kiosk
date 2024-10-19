"""This file holds the transaction model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from src.database.connection import Base

from sqlalchemy.orm import relationship

# Define the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    cost = Column(String, nullable=False)
    category = Column(String, nullable=False)

    item = relationship("Item")

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, category={self.category}, cost='{self.cost}')>"
        )

    def create(self, session):
        session.add(self)
        session.commit()

    @classmethod
    def read_all_for_user(cls, session, user_id):
        transactions = session.query(cls).filter(cls.user_id == user_id).all()
        return [
            (transaction.id, transaction.date, transaction.cost, transaction.category)
            for transaction in transactions
        ]