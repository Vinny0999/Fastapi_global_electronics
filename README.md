Global Electronics Retailer API

This project is a FastAPI-based web service for managing various components of an electronics retail business. It includes endpoints for Customers, Products, Sales, Stores, Exchange Rates, Categories, and Subcategories. The system utilizes an SQLite database with SQLModel as the ORM for structured data handling.

✨ Features

CRUD operations for Customers, Products, Sales, Stores and Exchange Rates
Pagination for optimized data retrieval
Date handling for fields like birthdays, order dates, and exchange rate timestamps
Uses SQLModel (a combination of Pydantic and SQLAlchemy) for data modeling
Fast and lightweight API with dependency injection for database sessions

⚒️ Development Notes

Ensure that the database is set up before running the API.
Always activate the virtual environment before running scripts.
Use uvicorn for local API testing.
Run populate_db.py whenever fresh test data is needed.
📚 License

This project is open-source and available under the MIT License.
