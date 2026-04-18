from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from disease_analyzer import LeafDiseaseAnalyzer
import shutil
import os
from pathlib import Path

app = FastAPI(title="Leaf Disease Detection API")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = LeafDiseaseAnalyzer()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Leaf Disease Detection API", "status": "active"}

@app.post("/analyze-leaf")
async def analyze_leaf(file: UploadFile = File(...)):
    """
    Analyze uploaded leaf image for diseases
    """
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # Analyze the image
    try:
        result = analyzer.analyze_leaf(str(file_path))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract structured data
        structured_data = analyzer.extract_structured_data(result["analysis"])
        
        return {
            "filename": file.filename,
            "analysis": result["analysis"],
            "structured_data": structured_data,
            "model_used": result["model"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

@app.get("/health")
def health_check():
    return {"status": "healthy"}