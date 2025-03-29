from sqlalchemy.orm import Session
from app.models.lab import Lab

def validate_lab_id(lab_id: str, db: Session) -> bool:
    """
    Validate that a lab ID exists in the database
    
    Args:
        lab_id: The lab ID to validate
        db: Database session
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not lab_id:
        return False
    
    lab = db.query(Lab).filter(Lab.lab_id == lab_id).first()
    return lab is not None

def validate_patient_id(patient_id: str) -> bool:
    """
    Validate that a patient ID is a valid 11-digit Medicare number
    
    Args:
        patient_id: The patient ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not patient_id:
        return False
    
    # Check if it's exactly 11 digits
    return len(patient_id) == 11 and patient_id.isdigit()