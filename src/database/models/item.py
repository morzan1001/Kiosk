"""This file holds the item model."""
from typing import List
from sqlalchemy import Column, Integer, String, Float, LargeBinary

from src.database.connection import Base

# Define the Item model
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(LargeBinary, nullable=True)  # For storing images as binary data
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"
    
    def create(self, session):
        session.add(self)
        session.commit()

    def update(self, session, name=None, price=None, category=None, quantity=None, barcode=None, image=None):
        if name:
            self.name = name
        if price:
            self.price = price
        if quantity:
            self.quantity = quantity
        if image:
            self.image = image
        if barcode:
            self.barcode = barcode
        if category:
            self.category = category
        session.commit()

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def read_all(cls, session) -> List['Item']:
        return session.query(cls).all()
    
    @classmethod
    def get_by_id(cls, session, item_id) -> 'Item':
        return session.query(cls).filter_by(id=item_id).first()

    @classmethod
    def get_count(cls, session) -> int:
        return session.query(cls).count()

    @classmethod
    def get_by_barcode(cls, session, barcode) -> 'Item':
        return session.query(cls).filter_by(barcode=barcode).first()