from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Category(Base):
  """
  Category Model - Represents food/drink categories.

  Attributes:
    id (Integer): Primary key
    name (Unique): Category name
    description (String): Category description
    items: Relationship to Item in this category
  """
  __tablename__ = "categories"

  id = Column(Integer, primary_key=True)
  name = Column(String(80), unique=True, nullable=False)
  description = Column(String(400))

  # Relationship: One category has many items
  items = relationship("Item", back_populates="category", cascade="all, delete-orphan")

  def __repr__(self):
    return f"<Category(id={self.id}, name='{self.name}')>"
  
class Item(Base):
  """
  Item Model - Represents food/drink items.

  Attributes:
    category_id: Foreign key to Category
    name: Item name
    description: Item description
    price: Item price
    rating: Rating (0.0 to 5.0)
    is_active: Whether item is available
    is_vegetarian (Boolean): Vegetarian flag
    created_at: Creation timestamp
    updated_at: Last update timestamp
  """
  __tablename__ = "items"

  id = Column(Integer, primary_key=True, index=True)
  category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
  name = Column(String(100), nullable=False, index=True)
  description = Column(String(500))
  price = Column(Float, nullable=False)
  rating = Column(Float, default=0.0)  # 0.0 to 5.0
  is_active = Column(Boolean, default=True)
  created_at = Column(DateTime, default=datetime.utcnow) # TODO: Use timezone-aware datetime
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  # Relationship: Many items belong to one category
  category = relationship("Category", back_populates="items")
  
  def __repr__(self):
      return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"