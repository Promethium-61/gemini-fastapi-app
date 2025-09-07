from .models import Department, Priority

# Priority mapping based on issue types
PRIORITY_MAPPING = {
    # Water Department
    "Pipe Burst": Priority.CRITICAL,
    "Low Pressure": Priority.MEDIUM,
    "Quality Issue": Priority.HIGH,
    "Meter Problem": Priority.LOW,
    "Billing Issue": Priority.LOW,
    
    # Roads Department
    "Pothole": Priority.HIGH,
    "Traffic Signal": Priority.CRITICAL,
    "Street Light": Priority.MEDIUM,
    "Road Damage": Priority.HIGH,
    "Drainage": Priority.MEDIUM,
    
    # Waste Management
    "Collection Delay": Priority.LOW,
    "Bin Overflow": Priority.MEDIUM,
    "Illegal Dumping": Priority.HIGH,
    "Recycling": Priority.LOW,
    "Hazardous Waste": Priority.CRITICAL,
    
    # Electricity Department
    "Power Outage": Priority.CRITICAL,
    "Voltage Issues": Priority.HIGH,
    "Meter Reading": Priority.LOW,
    "Billing": Priority.LOW,
    "Street Light Electricity": Priority.MEDIUM,
}

# Emergency contacts by department
EMERGENCY_CONTACTS = {
    Department.WATER: {
        "emergency": "+1-555-WATER-911",
        "maintenance": "+1-555-WATER-MNT",
        "billing": "+1-555-WATER-BILL"
    },
    Department.ROADS: {
        "emergency": "+1-555-ROADS-911",
        "maintenance": "+1-555-ROADS-MNT"
    },
    Department.WASTE: {
        "emergency": "+1-555-WASTE-911",
        "collection": "+1-555-WASTE-COLL"
    },
    Department.ELECTRICITY: {
        "emergency": "+1-555-POWER-911",
        "outage": "+1-555-POWER-OUT",
        "billing": "+1-555-POWER-BILL"
    }
}
