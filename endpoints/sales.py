from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query, Path

from config.env import get_session
from db.models import Sale
from sqlmodel import Session, select

# Dependency injection for database session
DatabaseSession = Annotated[Session, Depends(get_session)]

# Setting up API router with configurations
router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
    responses={
        status.HTTP_201_CREATED: {"description": "Successfully created the requested sale"},
        status.HTTP_404_NOT_FOUND: {"description": "Sale not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An internal server error occurred"},
    },
)

# ------ CRUD Operations ------

# ------ Create a new sale record ------
@router.post("/", response_model=Sale, summary="Add a new sale entry to the database")
def add_sale(sale: Sale, session: DatabaseSession):
    try:
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return sale
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error occurred: {error}")


# ------ Retrieve sale records ------

# Fetch a list of sale records
@router.get("/", response_model=dict, summary="Retrieve a list of sales")
def list_sales(
    session: DatabaseSession,
    response: Response,
    offset: Annotated[int, Query(description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(le=10, description="Maximum number of records to fetch")] = 5,
):
    sale_query = select(Sale).offset(offset).limit(limit)
    result_set = session.exec(sale_query)
    sale_list = result_set.all()
    
    return {"data": sale_list, "count": len(sale_list)}

# Retrieve details of a specific sale by ID
@router.get("/{sale_id}", response_model=Sale, summary="Retrieve details of a sale using its ID")
def fetch_sale_by_id(
    session: DatabaseSession,
    sale_id: Annotated[str, Path(description="Unique identifier of the sale")],
    response: Response,
):
    response.headers["Cache-Control"] = "no-cache"
    
    sale_query = select(Sale).where(Sale.OrderNumber == sale_id)
    result_set = session.exec(sale_query)
    sale_details = result_set.fetchall()
    
    if not sale_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Sale with ID {sale_id} not found"
        )
    
    return sale_details[0].model_dump()


# ------ Update sale records ------

# Full update of a sale's information
@router.put("/{sale_id}", response_model=Sale, status_code=status.HTTP_200_OK)
def modify_sale(
    session: DatabaseSession,
    sale_id: Annotated[str, Path(description="Sale ID to update")],
    sale: Sale,
):
    existing_sale = session.get(Sale, sale_id)
    if not existing_sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Sale with ID {sale_id} not found"
        )
    
    updated_data = sale.model_dump()
    existing_sale.sqlmodel_update(updated_data)
    session.add(existing_sale)
    session.commit()
    session.refresh(existing_sale)
    
    return existing_sale

# Partial update of a sale's information
@router.patch("/{sale_id}", response_model=Sale, status_code=status.HTTP_200_OK)
def update_sale_partially(
    session: DatabaseSession,
    sale_id: Annotated[str, Path(description="Sale ID to partially update")],
    sale: Sale,
):
    existing_sale = session.get(Sale, sale_id)
    if not existing_sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Sale with ID {sale_id} not found"
        )
    
    updated_data = sale.model_dump(exclude_unset=True)
    existing_sale.sqlmodel_update(updated_data)
    session.add(existing_sale)
    session.commit()
    session.refresh(existing_sale)
    
    return existing_sale
