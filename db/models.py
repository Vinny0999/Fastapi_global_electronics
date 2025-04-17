from typing import Optional
from sqlmodel import Field, SQLModel

class Customer(SQLModel, table=True):
    CustomerKey: int = Field(primary_key=True)
    Gender: str 
    Name: str
    City: str
    StateCode: str
    State: str
    ZipCode: str
    Country: str
    Continent: str
    Birthday: str

class Product(SQLModel, table=True):
    ProductKey : int = Field(primary_key=True)
    ProductName : str
    Brand : str
    Color : str
    UnitCostUSD : bool
    UnitPriceUSD : bool
    SubcategoryKey : str
    Subcategory : str
    CategoryKey : str
    Category : str


class Sale(SQLModel, table=True):
    OrderNumber: int = Field(primary_key=True)
    LineItem : int
    OrderDate : str
    DeliveryDate : str
    CustomerKey : int
    StoreKey : int
    ProductKey : int
    Quantity : int
    CurrencyCode : str



class Store(SQLModel, table=True):
    StoreKey : int = Field(primary_key=True)
    Country : str
    State : str
    SquareMeters : int
    OpenDate : str

class ExchangeRate(SQLModel, table=True):
    Date : str = Field(primary_key=True)
    Currency : str = Field(primary_key=True)
    Exchange : bool