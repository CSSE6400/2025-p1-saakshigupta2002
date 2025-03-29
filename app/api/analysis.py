from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
import base64
import os
import traceback

from app.database import get_db, Base, engine
from app.models.analysis import AnalysisJob
from app.services.analysis import validate_image, save_image, process_analysis
from app.utils.validation import validate_lab_id, validate_patient_id

router = APIRouter()

@router.get("/analysis")
async def get_analysis(
    request_id: str = Query(..., description="The analysis request identifier"),
    db: Session = Depends(get_db)
):
    """Get the result or current status of an analysis job"""
    # Find the analysis job
    analysis_job = db.query(AnalysisJob).filter(AnalysisJob.request_id == request_id).first()
    
    if not analysis_job:
        raise HTTPException(status_code=404, detail="Analysis request not found")
    
    # Return the analysis job details
    return {
        "request_id": analysis_job.request_id,
        "lab_id": analysis_job.lab_id,
        "patient_id": analysis_job.patient_id,
        "result": analysis_job.result,
        "urgent": analysis_job.urgent,
        "created_at": analysis_job.created_at,
        "updated_at": analysis_job.updated_at
    }

@router.post("/analysis", status_code=201)
async def create_analysis(
    patient_id: str = Query(..., description="The patient identifier"),
    lab_id: str = Query(..., description="The lab identifier"),
    urgent: bool = Query(False, description="Flag for urgent processing"),
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Request analysis of a sample"""
    # Validate patient ID (11-digit Medicare number)
    if not validate_patient_id(patient_id):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_patient_id",
                "detail": "Patient ID must be an 11-digit Medicare number"
            }
        )
    
    # Validate lab ID
    if not validate_lab_id(lab_id, db):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_lab_id",
                "detail": "Invalid lab identifier"
            }
        )
    
    try:
        if "image" not in payload:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "no_image",
                    "detail": "No image provided in the request"
                }
            )
        
        # Decode base64 image
        try:
            print("Attempting to decode base64 image...")
            image_data = base64.b64decode(payload["image"])
            print(f"Successfully decoded image, size: {len(image_data)} bytes")
        except Exception as e:
            print(f"Error decoding image: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_image",
                    "detail": f"Invalid base64 encoding: {str(e)}"
                }
            )
        
        # Validate image
        try:
            validate_image(image_data)
        except ValueError as e:
            print(f"Image validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "image_size" if "size" in str(e) else "invalid_image",
                    "detail": str(e)
                }
            )
        
        # Generate a unique ID for the analysis job
        request_id = str(uuid.uuid4())
        print(f"Generated request_id: {request_id}")
        
        # Save the image
        image_path = os.path.join("uploads", f"{request_id}.jpg")
        save_image(image_data, image_path)
        print(f"Image saved to {image_path}")
        
        # Create timestamp
        now = datetime.utcnow().isoformat() + "Z"
        
        # Create the analysis job
        analysis_job = AnalysisJob(
            request_id=request_id,
            patient_id=patient_id,
            lab_id=lab_id,
            image_path=image_path,
            urgent=urgent,
            created_at=now,
            updated_at=now,
            result="pending"
        )
        
        # Save to database
        db.add(analysis_job)
        db.commit()
        print(f"Analysis job created and saved to database with ID: {request_id}")
        
        # Process analysis
        print(f"Starting analysis for request_id: {request_id}")
        result = process_analysis(request_id, image_path)
        print(f"Analysis result: {result}")
        
        # Update the analysis job with the result
        analysis_job.result = result
        analysis_job.updated_at = datetime.utcnow().isoformat() + "Z"
        db.commit()
        print(f"Updated analysis job in database with result: {result}")
        
        # Return the response
        return {
            "id": request_id,
            "created_at": now,
            "updated_at": analysis_job.updated_at,
            "status": result  # Return the actual result instead of "pending"
        }
        
    except Exception as e:
        db.rollback()
        print(f"ERROR in create_analysis: {str(e)}")
        traceback.print_exc()  # Print full stack trace for debugging
        return JSONResponse(
            status_code=500,
            content={"error": "unknown_error", "detail": str(e)}
        )

@router.put("/analysis")
async def update_analysis(
    request_id: str = Query(..., description="The analysis request identifier"),
    lab_id: str = Query(..., description="The new lab identifier"),
    db: Session = Depends(get_db)
):
    """Update the lab associated with an analysis job"""
    # Validate lab ID
    if not validate_lab_id(lab_id, db):
        return JSONResponse(
            status_code=400,
            content="Invalid lab identifier"
        )
    
    # Find the analysis job
    analysis_job = db.query(AnalysisJob).filter(AnalysisJob.request_id == request_id).first()
    
    if not analysis_job:
        raise HTTPException(status_code=404, detail="Analysis request not found")
    
    # Update the lab ID
    analysis_job.lab_id = lab_id
    analysis_job.updated_at = datetime.utcnow().isoformat() + "Z"
    db.commit()
    
    # Return the updated analysis job
    return {
        "request_id": analysis_job.request_id,
        "lab_id": analysis_job.lab_id,
        "patient_id": analysis_job.patient_id,
        "result": analysis_job.result,
        "urgent": analysis_job.urgent,
        "created_at": analysis_job.created_at,
        "updated_at": analysis_job.updated_at
    }