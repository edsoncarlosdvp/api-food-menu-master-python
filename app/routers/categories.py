from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
  category: schemas.CategoryCreate,
  db: Session = Depends(get_db)
):
  """
  Create a new category.

  Args:
        category: Category data (name, description)
        db: Database session (injected)
    
    Returns:
        Created category with ID
    
    Raises:
        400: If category name already exists
  """

  # Check if category name already exists
  existing = db.query(models.Category).filter(
      models.Category.name == category.name
  ).first()
  
  if existing:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=f"Category with name '{category.name}' already exists"
      )
  
  # Create new category
  db_category = models.Category(**category.model_dump())
  db.add(db_category)
  db.commit()
  db.refresh(db_category)
  
  return db_category


@router.get("/", response_model=List[schemas.CategoryResponse])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all categories with pagination.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session (injected)
    
    Returns:
        List of categories
    """
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories


@router.get("/{category_id}", response_model=schemas.CategoryWithItems)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific category by ID, including its items.
    
    Args:
        category_id: Category ID
        db: Database session (injected)
    
    Returns:
        Category with all its items
    
    Raises:
        404: If category not found
    """
    category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return category


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a category.
    
    Args:
        category_id: Category ID
        category_update: Fields to update
        db: Database session (injected)
    
    Returns:
        Updated category
    
    Raises:
        404: If category not found
        400: If new name already exists
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    # Check if new name conflicts with existing category
    if category_update.name:
        existing = db.query(models.Category).filter(
            models.Category.name == category_update.name,
            models.Category.id != category_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_update.name}' already exists"
            )
    
    # Update fields
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a category.
    
    Args:
        category_id: Category ID
        db: Database session (injected)
    
    Returns:
        No content (204)
    
    Raises:
        404: If category not found
        400: If category has items
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    # Check if category has items
    if db_category.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {len(db_category.items)} items. Delete items first."
        )
    
    db.delete(db_category)
    db.commit()
    
    return None