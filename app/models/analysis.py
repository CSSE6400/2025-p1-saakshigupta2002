from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    request_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    lab_id = Column(String, index=True)
    image_path = Column(String)
    result = Column(String, default="pending")  # pending, covid, h5n1, healthy, failed
    urgent = Column(Boolean, default=False)
    created_at = Column(String)  # Store as ISO-8601 string with Z suffix
    updated_at = Column(String)  # Store as ISO-8601 string with Z suffix
