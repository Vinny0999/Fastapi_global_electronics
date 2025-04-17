from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query, Path

from config.env import get_session
from db.models import Product
from sqlmodel import Session, select

# Dependency injection for database session
DatabaseSession = Annotated[Session, Depends(get_session)]

# Configuring the API router with necessary settings
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={
        status.HTTP_201_CREATED: {"description": "Successfully created the requested product"},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An error occurred on the server"},
    },
)

# ------ CRUD Operations ------

# ------ Create a new product record ------
@router.post("/", response_model=Product, summary="Add a new product entry to the database")
def add_product(product: Product, session: DatabaseSession):
    try:
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error occurred: {error}")


# ------ Retrieve product records ------

# Fetch a list of product records
@router.get("/", response_model=dict, summary="Retrieve a list of products")
def list_products(
    session: DatabaseSession,
    response: Response,
    offset: Annotated[int, Query(description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(le=10, description="Maximum number of records to fetch")] = 5,
):
    product_query = select(Product).offset(offset).limit(limit)
    result_set = session.exec(product_query)
    product_list = result_set.all()
    
    return {"data": product_list, "count": len(product_list)}

# Retrieve details of a specific product by ID
@router.get("/{product_id}", response_model=Product, summary="Retrieve details of a product using its ID")
def fetch_product_by_id(
    session: DatabaseSession,
    product_id: Annotated[str, Path(description="Unique identifier of the product")],
    response: Response,
):
    response.headers["Cache-Control"] = "no-cache"
    
    product_query = select(Product).where(Product.ProductKey == product_id)
    result_set = session.exec(product_query)
    product_details = result_set.fetchall()
    
    if not product_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found"
        )
    
    return product_details[0].model_dump()


# ------ Update product records ------

# Full update of a product's information
@router.put("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
def modify_product(
    session: DatabaseSession,
    product_id: Annotated[str, Path(description="Product ID to update")],
    product: Product,
):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found"
        )
    
    updated_data = product.model_dump()
    existing_product.sqlmodel_update(updated_data)
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    
    return existing_product

# Partial update of a product's information
@router.patch("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
def update_product_partially(
    session: DatabaseSession,
    product_id: Annotated[str, Path(description="Product ID to partially update")],
    product: Product,
):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found"
        )
    
    updated_data = product.model_dump(exclude_unset=True)
    existing_product.sqlmodel_update(updated_data)
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    
    return existing_product
