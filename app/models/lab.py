from sqlalchemy import Column, String
from app.database import Base

class Lab(Base):
    __tablename__ = "labs"
    
    lab_id = Column(String, primary_key=True, index=True)
