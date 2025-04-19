from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .ocr_processor import ocr_extract

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



@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to receive binary file and return OCR results
    """
    try:
        data = await file.read()
        text = ocr_extract(data)
        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")



def run_service():
    """
    Run the FastAPI service
    """
    uvicorn.run("service.service:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run_service()