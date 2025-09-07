from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .models import ComplaintRequest, ComplaintResponse, Tag, Department, Priority, DepartmentInfo
from .gemini_api_client import GeminiAPIClient
from .config import settings
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Urban Infrastructure Complaint Analyzer",
    description="AI-powered system for analyzing urban infrastructure complaints and routing them to appropriate departments",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini API client
try:
    gemini_client = GeminiAPIClient()
    logger.info("Gemini API client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini API client: {e}")
    gemini_client = None

# Department information database
DEPARTMENT_INFO = {
    Department.WATER: DepartmentInfo(
        name="Water Department",
        contact_email="water@city.gov",
        contact_phone="+1-555-WATER",
        response_time="24-48 hours",
        common_issues=["Pipe bursts", "Water quality", "Pressure issues", "Meter problems"]
    ),
    Department.ROADS: DepartmentInfo(
        name="Roads and Transportation Department",
        contact_email="roads@city.gov",
        contact_phone="+1-555-ROADS",
        response_time="12-24 hours",
        common_issues=["Potholes", "Road damage", "Traffic signals", "Street lights"]
    ),
    Department.WASTE: DepartmentInfo(
        name="Waste Management Department",
        contact_email="waste@city.gov",
        contact_phone="+1-555-WASTE",
        response_time="24-72 hours",
        common_issues=["Collection delays", "Bin overflow", "Illegal dumping", "Recycling"]
    ),
    Department.ELECTRICITY: DepartmentInfo(
        name="Electricity Department",
        contact_email="electricity@city.gov",
        contact_phone="+1-555-POWER",
        response_time="2-12 hours",
        common_issues=["Power outages", "Voltage issues", "Meter problems", "Billing"]
    ),
    Department.OTHER: DepartmentInfo(
        name="General Services",
        contact_email="services@city.gov",
        contact_phone="+1-555-CITY",
        response_time="48-72 hours",
        common_issues=["General complaints", "Other municipal issues"]
    )
}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

@app.post("/analyze-complaint", response_model=ComplaintResponse)
async def analyze_complaint(request: ComplaintRequest):
    """
    Analyze an urban infrastructure complaint with image and description.
    Returns tags, department, priority, image description, and match verification.
    """
    try:
        if not gemini_client:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        # Validate image data
        if not request.image_data.startswith('data:image/'):
            raise HTTPException(status_code=400, detail="Invalid image format. Expected base64 encoded image.")
        
        # Extract base64 data (remove data:image/... prefix)
        image_data = request.image_data.split(',')[1] if ',' in request.image_data else request.image_data
        
        # Analyze with Gemini API
        result = gemini_client.analyze_image(image_data, request.description)
        
        return ComplaintResponse(
            tags=result['tags'],
            department=result['department'],
            priority=result['priority'],
            image_description=result['image_description'],
            description_match=result['description_match'],
            confidence_score=result.get('confidence_score', 0.5),
            suggested_actions=result.get('suggested_actions', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-text", response_model=ComplaintResponse)
async def analyze_text_only(description: str):
    """
    Analyze complaint description only (without image)
    """
    try:
        if not gemini_client:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        result = gemini_client.analyze_text_only(description)
        
        return ComplaintResponse(
            tags=result['tags'],
            department=result['department'],
            priority=result['priority'],
            image_description=result['image_description'],
            description_match=result['description_match'],
            confidence_score=result.get('confidence_score', 0.5),
            suggested_actions=result.get('suggested_actions', [])
        )
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "service": "Urban Infrastructure Analyzer",
        "gemini_available": gemini_client is not None,
        "api_version": "v2.0.0",
        "supported_models": ["gemini-2.0-flash"]
    }
    return status

@app.get("/tags")
async def get_available_tags():
    """Get available tags organized by department"""
    return {
        "water_department": [tag.value for tag in Tag if tag.value in [
            "Pipe Burst", "Low Pressure", "Quality Issue", "Meter Problem", "Billing Issue"
        ]],
        "roads_department": [tag.value for tag in Tag if tag.value in [
            "Pothole", "Traffic Signal", "Street Light", "Road Damage", "Drainage"
        ]],
        "waste_management": [tag.value for tag in Tag if tag.value in [
            "Collection Delay", "Bin Overflow", "Illegal Dumping", "Recycling", "Hazardous Waste"
        ]],
        "electricity_department": [tag.value for tag in Tag if tag.value in [
            "Power Outage", "Voltage Issues", "Meter Reading", "Billing", "Street Light Electricity"
        ]]
    }

@app.get("/departments")
async def get_available_departments():
    """Get available departments with contact information"""
    return {dept.value: info.dict() for dept, info in DEPARTMENT_INFO.items()}

@app.get("/priorities")
async def get_available_priorities():
    """Get available priorities"""
    return {"priorities": [priority.value for priority in Priority]}

@app.get("/department/{department_name}/info")
async def get_department_info(department_name: Department):
    """Get detailed information for a specific department"""
    if department_name in DEPARTMENT_INFO:
        return DEPARTMENT_INFO[department_name]
    raise HTTPException(status_code=404, detail="Department not found")

@app.get("/tags/{department_name}")
async def get_tags_by_department(department_name: Department):
    """Get tags for a specific department"""
    department_tags = {
        Department.WATER: [Tag.PIPE_BURST, Tag.LOW_PRESSURE, Tag.QUALITY_ISSUE, Tag.METER_PROBLEM, Tag.BILLING_ISSUE],
        Department.ROADS: [Tag.POTHOLE, Tag.TRAFFIC_SIGNAL, Tag.STREET_LIGHT, Tag.ROAD_DAMAGE, Tag.DRAINAGE],
        Department.WASTE: [Tag.COLLECTION_DELAY, Tag.BIN_OVERFLOW, Tag.ILLEGAL_DUMPING, Tag.RECYCLING, Tag.HAZARDOUS_WASTE],
        Department.ELECTRICITY: [Tag.POWER_OUTAGE, Tag.VOLTAGE_ISSUES, Tag.METER_READING, Tag.BILLING, Tag.STREET_LIGHT_ELECTRICITY]
    }
    
    if department_name in department_tags:
        return {"department": department_name.value, "tags": [tag.value for tag in department_tags[department_name]]}
    
    return {"department": department_name.value, "tags": []}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Urban Infrastructure Complaint Analyzer API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze_complaint": "/analyze-complaint",
            "analyze_text": "/analyze-text",
            "health": "/health",
            "tags": "/tags",
            "departments": "/departments",
            "priorities": "/priorities"
        },
        "status": "operational" if gemini_client else "initializing"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info" if settings.DEBUG else "warning"
    )