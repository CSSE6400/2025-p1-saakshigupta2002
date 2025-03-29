from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.analysis import AnalysisJob
from app.utils.validation import validate_patient_id

router = APIRouter()

@router.get("/patients/results")
async def get_patient_results(
    patient_id: str = Query(..., description="The patient identifier"),
    start: Optional[str] = None,
    end: Optional[str] = None,
    status: Optional[str] = None,
    urgent: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all analysis jobs associated with a patient"""
    # Validate patient_id (11-digit Medicare number)
    if not validate_patient_id(patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient identifier")
    
    # Query analysis jobs for this patient
    query = db.query(AnalysisJob).filter(AnalysisJob.patient_id == patient_id)
    
    # Apply filters
    if start:
        query = query.filter(AnalysisJob.created_at >= start)
    if end:
        query = query.filter(AnalysisJob.created_at <= end)
    if status:
        query = query.filter(AnalysisJob.result == status)
    if urgent is not None:
        query = query.filter(AnalysisJob.urgent == urgent)
    
    # Get the results
    jobs = query.all()
    
    # If no jobs found for this patient, still return empty array (not 404)
    
    # Format the results
    results = []
    for job in jobs:
        results.append({
            "request_id": job.request_id,
            "lab_id": job.lab_id,
            "patient_id": job.patient_id,
            "result": job.result,
            "urgent": job.urgent,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        })
    
    return results