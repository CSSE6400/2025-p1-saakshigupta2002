from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import requests

from app.database import get_db
from app.models.analysis import AnalysisJob
from app.models.lab import Lab
from app.utils.validation import validate_lab_id

router = APIRouter()

@router.get("/labs")
async def get_labs(db: Session = Depends(get_db)):
    """List all labs with permission to use this service"""
    # Get all labs from the database
    labs = db.query(Lab).all()
    return [lab.lab_id for lab in labs]

@router.get("/labs/results/{lab_id}")
async def get_lab_results(
    lab_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    start: Optional[str] = None,
    end: Optional[str] = None,
    patient_id: Optional[str] = None,
    status: Optional[str] = None,
    urgent: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all analysis jobs associated with a lab"""
    # Validate the lab_id
    if not validate_lab_id(lab_id, db):
        raise HTTPException(status_code=404, detail="Lab identifier does not correspond to a known lab")
    
    # Query analysis jobs for this lab
    query = db.query(AnalysisJob).filter(AnalysisJob.lab_id == lab_id)
    
    # Apply filters
    if start:
        query = query.filter(AnalysisJob.created_at >= start)
    if end:
        query = query.filter(AnalysisJob.created_at <= end)
    if patient_id:
        query = query.filter(AnalysisJob.patient_id == patient_id)
    if status:
        query = query.filter(AnalysisJob.result == status)
    if urgent is not None:
        query = query.filter(AnalysisJob.urgent == urgent)
    
    # Apply pagination
    total = query.count()
    jobs = query.offset(offset).limit(limit).all()
    
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

@router.get("/labs/results/{lab_id}/summary")
async def get_lab_summary(
    lab_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Summary of analysis jobs associated with this lab"""
    # Validate the lab_id
    if not validate_lab_id(lab_id, db):
        raise HTTPException(status_code=404, detail="Lab identifier does not correspond to a known lab")
    
    # Query analysis jobs for this lab
    query = db.query(AnalysisJob).filter(AnalysisJob.lab_id == lab_id)
    
    # Apply date filters
    if start:
        query = query.filter(AnalysisJob.created_at >= start)
    if end:
        query = query.filter(AnalysisJob.created_at <= end)
    
    # Count by status
    pending_count = query.filter(AnalysisJob.result == "pending").count()
    covid_count = query.filter(AnalysisJob.result == "covid").count()
    h5n1_count = query.filter(AnalysisJob.result == "h5n1").count()
    healthy_count = query.filter(AnalysisJob.result == "healthy").count()
    failed_count = query.filter(AnalysisJob.result == "failed").count()
    urgent_count = query.filter(AnalysisJob.urgent == True).count()
    
    return {
        "lab_id": lab_id,
        "pending": pending_count,
        "covid": covid_count,
        "h5n1": h5n1_count,
        "healthy": healthy_count,
        "failed": failed_count,
        "urgent": urgent_count,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }