"""This file holds the transaction model."""
from sqlalchemy import Column, Integer, String

from src.database.connection import Base

# Define the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    category = Column(String, nullable=False)


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