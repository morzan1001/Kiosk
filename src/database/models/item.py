"""This file holds the item model."""

from typing import List

from sqlalchemy import Column, Float, Integer, LargeBinary, String

from src.database.connection import Base
from src.database.crud_mixin import CRUDMixin


# Define the Item model
class Item(Base, CRUDMixin):
    __tablename__ = "items"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(LargeBinary, nullable=True)  # For storing images as binary data
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"

    @classmethod
    def get_by_id(cls, session, item_id) -> "Item":
        return session.query(cls).filter_by(id=item_id).first()

    @classmethod
    def get_count(cls, session) -> int:
        return session.query(cls).count()

    @classmethod
    def get_by_barcode(cls, session, barcode) -> "Item":
        return session.query(cls).filter_by(barcode=barcode).first()
