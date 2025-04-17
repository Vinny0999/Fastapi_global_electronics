from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from endpoints import customers
from endpoints import products
from endpoints import sales
from endpoints import stores
from endpoints import exchangerate


description = """
This API helps interact with the Global Electronics Retailer database.

It allows to:

👉 **List all customers, stores, sales, products, and exchange rates**

👉 **Perform CRUD operations on various entities**

Further Information is below 👇
"""

app = FastAPI(
    title="Global Electronics Retailer API",
    description=description,
    summary="🎯 API to interact with the Global Electronics Retailer database",
    version="1.0.0",
    contact={"name": "Vinay Kumar",
             "url": "https://vinaykumar99.netlify.app/",
             "email": "vinay.kumar@epita.fr"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

templates = Jinja2Templates(directory="templates")

app.include_router(customers.router)
app.include_router(sales.router)
app.include_router(stores.router)
app.include_router(products.router)
app.include_router(exchangerate.router)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})