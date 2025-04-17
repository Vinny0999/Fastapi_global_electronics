from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query, Path

from config.env import get_session
from db.models import Store
from sqlmodel import Session, select

# Dependency injection for database session
DatabaseSession = Annotated[Session, Depends(get_session)]

# Setting up API router with configurations
router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
    responses={
        status.HTTP_201_CREATED: {"description": "Successfully created the requested store"},
        status.HTTP_404_NOT_FOUND: {"description": "Store not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An internal server error occurred"},
    },
)

# ------ CRUD Operations ------

# ------ Create a new store record ------
@router.post("/", response_model=Store, summary="Add a new store entry to the database")
def add_store(store: Store, session: DatabaseSession):
    try:
        session.add(store)
        session.commit()
        session.refresh(store)
        return store
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error occurred: {error}")


# ------ Retrieve store records ------

# Fetch a list of store records
@router.get("/", response_model=dict, summary="Retrieve a list of stores")
def list_stores(
    session: DatabaseSession,
    response: Response,
    offset: Annotated[int, Query(description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(le=10, description="Maximum number of records to fetch")] = 5,
):
    store_query = select(Store).offset(offset).limit(limit)
    result_set = session.exec(store_query)
    store_list = result_set.all()
    
    return {"data": store_list, "count": len(store_list)}

# Retrieve details of a specific store by ID
@router.get("/{store_id}", response_model=Store, summary="Retrieve details of a store using its ID")
def fetch_store_by_id(
    session: DatabaseSession,
    store_id: Annotated[str, Path(description="Unique identifier of the store")],
    response: Response,
):
    response.headers["Cache-Control"] = "no-cache"
    
    store_query = select(Store).where(Store.StoreKey == store_id)
    result_set = session.exec(store_query)
    store_details = result_set.fetchall()
    
    if not store_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Store with ID {store_id} not found"
        )
    
    return store_details[0].model_dump()


# ------ Update store records ------

# Full update of a store's information
@router.put("/{store_id}", response_model=Store, status_code=status.HTTP_200_OK)
def modify_store(
    session: DatabaseSession,
    store_id: Annotated[str, Path(description="Store ID to update")],
    store: Store,
):
    existing_store = session.get(Store, store_id)
    if not existing_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Store with ID {store_id} not found"
        )
    
    updated_data = store.model_dump()
    existing_store.sqlmodel_update(updated_data)
    session.add(existing_store)
    session.commit()
    session.refresh(existing_store)
    
    return existing_store

# Partial update of a store's information
@router.patch("/{store_id}", response_model=Store, status_code=status.HTTP_200_OK)
def update_store_partially(
    session: DatabaseSession,
    store_id: Annotated[str, Path(description="Store ID to partially update")],
    store: Store,
):
    existing_store = session.get(Store, store_id)
    if not existing_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Store with ID {store_id} not found"
        )
    
    updated_data = store.model_dump(exclude_unset=True)
    existing_store.sqlmodel_update(updated_data)
    session.add(existing_store)
    session.commit()
    session.refresh(existing_store)
    
    return existing_store
