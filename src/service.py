from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models.orders import MatchRequest
from utils.fuzzy_matcher import match_items

app = FastAPI(
    title="Invoice Agent Service",
    description="A service to process invoices using the Invoice Agent.",
    version="1.0.0",
)

# Different domain/port for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/match-products")
async def match_products(payload: MatchRequest):
    result = match_items(payload.items, payload.product_list)
    result["customer_name"] = payload.customer_name
    result["order_date"] = payload.order_date
    return result


def run_service():
    """
    Run the FastAPI service
    """
    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_service()