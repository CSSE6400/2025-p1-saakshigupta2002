import csv
import os
import requests
from sqlalchemy.orm import Session
from app.models.lab import Lab

def load_labs(db: Session):
    """Load the list of labs from the CSV file"""
    try:
        csv_data = None
        
        # First try to load from local file
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "labs.csv")
        if os.path.exists(local_path):
            print(f"Loading labs from local file: {local_path}")
            with open(local_path, "r") as f:
                csv_data = f.read().splitlines()
        elif os.path.exists("/app/labs.csv"):
            print("Loading labs from /app/labs.csv")
            with open("/app/labs.csv", "r") as f:
                csv_data = f.read().splitlines()
        else:
            # Fall back to downloading from URL
            print("Loading labs from remote URL")
            response = requests.get("https://csse6400.uqcloud.net/resources/labs.csv")
            response.raise_for_status()
            csv_data = response.text.splitlines()
        
        if not csv_data:
            print("No lab data found")
            return False
            
        # Parse the CSV data
        reader = csv.reader(csv_data)
        # Try to detect if there's a header row
        has_header = False
        try:
            first_row = next(reader)
            # If the first row doesn't look like a lab ID, consider it a header
            if first_row and first_row[0] and (not first_row[0].isalnum() or len(first_row[0]) < 3):
                has_header = True
            # Reset the reader
            reader = csv.reader(csv_data)
            if has_header:
                next(reader)  # Skip header
        except StopIteration:
            # Empty file
            return False
        
        # Count labs before adding
        lab_count_before = db.query(Lab).count()
        
        # Add labs to the database
        labs_added = 0
        for row in reader:
            if row and row[0]:  # Make sure there's a lab ID
                lab_id = row[0].strip()
                # Check if lab already exists to avoid duplicates
                existing_lab = db.query(Lab).filter(Lab.lab_id == lab_id).first()
                if not existing_lab:
                    lab = Lab(lab_id=lab_id)
                    db.add(lab)
                    labs_added += 1
        
        if labs_added > 0:
            db.commit()
            
        lab_count_after = db.query(Lab).count()
        print(f"Labs loaded. Added {labs_added} new labs. Total labs: {lab_count_after}")
        return True
    except Exception as e:
        print(f"Error loading labs: {e}")
        db.rollback()
        return False