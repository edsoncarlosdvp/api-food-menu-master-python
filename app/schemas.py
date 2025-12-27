from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel):
  """Base schema for Category - shared fields"""
  name: str = Field(..., min_length=3, max_length=80, description="Name of the category")
  description: Optional[str] = Field(None, max_length=400, description="Description of the category")

class CategoryCreate(CategoryBase):
  """Schema for creating a new Category"""
  pass

class CategoryUpdate(BaseModel):
  """Schema for updating an existing Category"""
  name: Optional[str] = Field(None, min_length=3, max_length=80)
  description: Optional[str] = Field(None, max_length=400)

class CategoryResponse(CategoryBase):
  """Schema for Category response - includes database fields"""
  id: int

  class Config:
    from_attributes = True

class CategoryWithItems(CategoryResponse):
  """Schema for Category with its items"""
  items: List["ItemResponse"] = []

class ItemBase(BaseModel):
    """Base schema for Item - shared fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    rating: Optional[float] = Field(0.0, ge=0.0, le=5.0, description="Rating from 0.0 to 5.0")
    is_active: bool = Field(True, description="Whether item is available")
  
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Ensure price has max 2 decimal places"""
        if round(v, 2) != v:
            raise ValueError('Price must have at most 2 decimal places')
        return v
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        """Ensure rating is within valid range"""
        if v is not None and (v < 0.0 or v > 5.0):
            raise ValueError('Rating must be between 0.0 and 5.0')
        return v


class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    category_id: int = Field(..., gt=0, description="Category ID")


class ItemUpdate(BaseModel):
    """Schema for updating an item - all fields optional"""
    category_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None


class ItemResponse(ItemBase):
    """Schema for item response - includes database fields"""
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemWithCategory(ItemResponse):
    """Schema for item with its category information"""
    category: CategoryResponse