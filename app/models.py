from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Tag(str, Enum):
    # Water Department
    PIPE_BURST = "Pipe Burst"
    LOW_PRESSURE = "Low Pressure"
    QUALITY_ISSUE = "Quality Issue"
    METER_PROBLEM = "Meter Problem"
    BILLING_ISSUE = "Billing Issue"
    
    # Roads Department
    POTHOLE = "Pothole"
    TRAFFIC_SIGNAL = "Traffic Signal"
    STREET_LIGHT = "Street Light"
    ROAD_DAMAGE = "Road Damage"
    DRAINAGE = "Drainage"
    
    # Waste Management
    COLLECTION_DELAY = "Collection Delay"
    BIN_OVERFLOW = "Bin Overflow"
    ILLEGAL_DUMPING = "Illegal Dumping"
    RECYCLING = "Recycling"
    HAZARDOUS_WASTE = "Hazardous Waste"
    
    # Electricity Department
    POWER_OUTAGE = "Power Outage"
    VOLTAGE_ISSUES = "Voltage Issues"
    METER_READING = "Meter Reading"
    BILLING = "Billing"
    STREET_LIGHT_ELECTRICITY = "Street Light Electricity"
    
    # General
    OTHER = "Other"

class Department(str, Enum):
    WATER = "water"
    ROADS = "roads"
    WASTE = "waste"
    ELECTRICITY = "electricity"
    OTHER = "other"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplaintRequest(BaseModel):
    description: str
    image_data: str  # Base64 encoded image

class ComplaintResponse(BaseModel):
    tags: List[Tag]
    department: Department
    priority: Priority
    image_description: str
    description_match: bool
    confidence_score: float
    suggested_actions: List[str]

class DepartmentInfo(BaseModel):
    name: str
    contact_email: str
    contact_phone: str
    response_time: str
    common_issues: List[str]