from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas

# Create router for item endpoints
router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new menu item.
    
    Args:
        item: Item data
        db: Database session (injected)
    
    Returns:
        Created item with ID and timestamps
    
    Raises:
        404: If category doesn't exist
    """
    # Verify category exists
    category = db.query(models.Category).filter(
        models.Category.id == item.category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {item.category_id} not found"
        )
    
    # Create new item
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item


@router.get("/", response_model=List[schemas.ItemResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    db: Session = Depends(get_db)
):
    """
    List menu items with filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        category_id: Filter by category (optional)
        is_active: Filter by active status (optional)
        min_price: Minimum price filter (optional)
        max_price: Maximum price filter (optional)
        min_rating: Minimum rating filter (optional)
        db: Database session (injected)
    
    Returns:
        List of items matching filters
    """
    query = db.query(models.Item)
    
    # Apply filters
    if category_id is not None:
        query = query.filter(models.Item.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(models.Item.is_active == is_active)
    
    if min_price is not None:
        query = query.filter(models.Item.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Item.price <= max_price)
    
    if min_rating is not None:
        query = query.filter(models.Item.rating >= min_rating)
    
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=schemas.ItemWithCategory)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific item by ID, including its category.
    
    Args:
        item_id: Item ID
        db: Database session (injected)
    
    Returns:
        Item with category information
    
    Raises:
        404: If item not found
    """
    item = db.query(models.Item).filter(
        models.Item.id == item_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    return item


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a menu item.
    
    Args:
        item_id: Item ID
        item_update: Fields to update
        db: Database session (injected)
    
    Returns:
        Updated item
    
    Raises:
        404: If item or new category not found
    """
    db_item = db.query(models.Item).filter(
        models.Item.id == item_id
    ).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # If updating category, verify it exists
    if item_update.category_id:
        category = db.query(models.Category).filter(
            models.Category.id == item_update.category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {item_update.category_id} not found"
            )
    
    # Update fields
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a menu item.
    
    Args:
        item_id: Item ID
        db: Database session (injected)
    
    Returns:
        No content (204)
    
    Raises:
        404: If item not found
    """
    db_item = db.query(models.Item).filter(
        models.Item.id == item_id
    ).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    db.delete(db_item)
    db.commit()
    
    return None


@router.patch("/{item_id}/toggle-active", response_model=schemas.ItemResponse)
def toggle_item_active(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle item active status (convenience endpoint).
    
    Args:
        item_id: Item ID
        db: Database session (injected)
    
    Returns:
        Updated item
    
    Raises:
        404: If item not found
    """
    db_item = db.query(models.Item).filter(
        models.Item.id == item_id
    ).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    db_item.is_active = not db_item.is_active
    db.commit()
    db.refresh(db_item)
    
    return db_item