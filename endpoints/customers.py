from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query, Path

from config.env import get_session
from db.models import Customer
from sqlmodel import Session, select

# Dependency injection for database session
DatabaseSession = Annotated[Session, Depends(get_session)]

# Setting up the API router with prefixes and status codes
router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={
        status.HTTP_201_CREATED: {"description": "Successfully created the requested resource"},
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An error occurred on the server"},
    },
)

# ------ CRUD Operations ------

# ------ Create a new customer record ------
@router.post("/", response_model=Customer, summary="Add a new customer entry to the database")
def add_customer(customer: Customer, session: DatabaseSession):
    try:
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error occurred: {error}")


# ------ Retrieve customer records ------

# Fetch a list of customer records
@router.get("/", response_model=dict, summary="Retrieve a list of customers")
def list_customers(
    session: DatabaseSession,
    response: Response,
    offset: Annotated[int, Query(description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(le=10, description="Maximum number of records to fetch")] = 5,
):
    customer_query = select(Customer).offset(offset).limit(limit)
    result_set = session.exec(customer_query)
    customer_list = result_set.all()
    
    return {"data": customer_list, "count": len(customer_list)}

# Retrieve details of a specific customer by ID
@router.get("/{customer_id}", response_model=Customer, summary="Retrieve details of a customer using their ID")
def fetch_customer_by_id(
    session: DatabaseSession,
    customer_id: Annotated[str, Path(description="Unique identifier of the customer")],
    response: Response,
):
    response.headers["Cache-Control"] = "no-cache"
    
    customer_query = select(Customer).where(Customer.CustomerKey == customer_id)
    result_set = session.exec(customer_query)
    customer_details = result_set.fetchall()
    
    if not customer_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {customer_id} not found"
        )
    
    return customer_details[0].model_dump()


# ------ Update customer records ------

# Full update of a customer's information
@router.put("/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
def modify_customer(
    session: DatabaseSession,
    customer_id: Annotated[str, Path(description="ID of the customer to update")],
    customer: Customer,
):
    existing_customer = session.get(Customer, customer_id)
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {customer_id} not found"
        )
    
    updated_data = customer.model_dump()
    existing_customer.sqlmodel_update(updated_data)
    session.add(existing_customer)
    session.commit()
    session.refresh(existing_customer)
    
    return existing_customer

# Partial update of a customer's information
@router.patch("/{customer_id}", response_model=Customer, status_code=status.HTTP_200_OK)
def update_customer_partially(
    session: DatabaseSession,
    customer_id: Annotated[str, Path(description="ID of the customer to partially update")],
    customer: Customer,
):
    existing_customer = session.get(Customer, customer_id)
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with ID {customer_id} not found"
        )
    
    updated_data = customer.model_dump(exclude_unset=True)
    existing_customer.sqlmodel_update(updated_data)
    session.add(existing_customer)
    session.commit()
    session.refresh(existing_customer)
    
    return existing_customer
