from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query, Path

from config.env import get_session
from db.models import ExchangeRate
from sqlmodel import Session, select

# Dependency injection for database session
DatabaseSession = Annotated[Session, Depends(get_session)]

# Initializing API router with relevant configurations
router = APIRouter(
    prefix="/exchangerates",
    tags=["ExchangeRate"],
    responses={
        status.HTTP_201_CREATED: {"description": "Successfully created the requested resource"},
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "An error occurred on the server"},
    },
)

# ------ CRUD Operations ------

# ------ Create a new exchange rate record ------
@router.post("/", response_model=ExchangeRate, summary="Add a new exchange rate entry to the database")
def add_exchange_rate(exchange_rate: ExchangeRate, session: DatabaseSession):
    try:
        session.add(exchange_rate)
        session.commit()
        session.refresh(exchange_rate)
        return exchange_rate
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error occurred: {error}")


# ------ Retrieve exchange rate records ------

# Fetch a list of exchange rate records
@router.get("/", response_model=dict, summary="Retrieve a list of exchange rates")
def list_exchange_rates(
    session: DatabaseSession,
    response: Response,
    offset: Annotated[int, Query(description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(le=10, description="Maximum number of records to fetch")] = 5,
):
    exchange_rate_query = select(ExchangeRate).offset(offset).limit(limit)
    result_set = session.exec(exchange_rate_query)
    exchange_rate_list = result_set.all()
    
    return {"data": exchange_rate_list, "count": len(exchange_rate_list)}

# Retrieve details of a specific exchange rate by currency
@router.get("/{currency}", response_model=ExchangeRate, summary="Retrieve details of an exchange rate using currency")
def fetch_exchange_rate_by_currency(
    session: DatabaseSession,
    currency: Annotated[str, Path(description="Unique identifier of the exchange rate")],
    response: Response,
):
    response.headers["Cache-Control"] = "no-cache"
    
    exchange_rate_query = select(ExchangeRate).where(ExchangeRate.Currency == currency)
    result_set = session.exec(exchange_rate_query)
    exchange_rate_details = result_set.fetchall()
    
    if not exchange_rate_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Exchange rate with currency {currency} not found"
        )
    
    return exchange_rate_details[0].model_dump()


# ------ Update exchange rate records ------

# Full update of an exchange rate's information
@router.put("/{currency}", response_model=ExchangeRate, status_code=status.HTTP_200_OK)
def modify_exchange_rate(
    session: DatabaseSession,
    currency: Annotated[str, Path(description="Currency identifier of the exchange rate to update")],
    exchange_rate: ExchangeRate,
):
    existing_exchange_rate = session.get(ExchangeRate, currency)
    if not existing_exchange_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Exchange rate with currency {currency} not found"
        )
    
    updated_data = exchange_rate.model_dump()
    existing_exchange_rate.sqlmodel_update(updated_data)
    session.add(existing_exchange_rate)
    session.commit()
    session.refresh(existing_exchange_rate)
    
    return existing_exchange_rate

# Partial update of an exchange rate's information
@router.patch("/{currency}", response_model=ExchangeRate, status_code=status.HTTP_200_OK)
def update_exchange_rate_partially(
    session: DatabaseSession,
    currency: Annotated[str, Path(description="Currency identifier of the exchange rate to partially update")],
    exchange_rate: ExchangeRate,
):
    existing_exchange_rate = session.get(ExchangeRate, currency)
    if not existing_exchange_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Exchange rate with currency {currency} not found"
        )
    
    updated_data = exchange_rate.model_dump(exclude_unset=True)
    existing_exchange_rate.sqlmodel_update(updated_data)
    session.add(existing_exchange_rate)
    session.commit()
    session.refresh(existing_exchange_rate)
    
    return existing_exchange_rate
