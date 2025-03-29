import os
import subprocess
import json
import base64
from datetime import datetime
import uuid
from io import BytesIO
from PIL import Image

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"

def validate_image(image_data):
    """Validate the image (size and format)"""
    # Check size (between 4KB and 150KB)
    size_kb = len(image_data) / 1024
    if size_kb < 4:
        raise ValueError(f"Image too small (<4KB). Size: {size_kb:.2f}KB")
    if size_kb > 150:
        raise ValueError(f"Image too large (>150KB). Size: {size_kb:.2f}KB")
    
    # Check format (should be JPEG)
    try:
        with BytesIO(image_data) as img_io:
            img = Image.open(img_io)
            if img.format != "JPEG":
                raise ValueError(f"Invalid image format. Expected JPEG, got {img.format}")
    except Exception as e:
        raise ValueError(f"Invalid image: {str(e)}")
    
    return True

def save_image(image_data, path):
    """Save the image to disk"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(image_data)
    return path

def process_analysis(request_id, image_path):
    """Process the analysis using overflowengine"""
    output_path = os.path.join(RESULT_DIR, f"{request_id}.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Get absolute paths and check permissions
        abs_image_path = os.path.abspath(image_path)
        abs_output_path = os.path.abspath(output_path)
        
        print(f"Processing analysis for request_id: {request_id}")
        print(f"Image path: {abs_image_path}")
        print(f"Output path: {abs_output_path}")
        
        # Check if image exists and is readable
        if not os.path.exists(abs_image_path):
            print(f"Error: Image file does not exist at {abs_image_path}")
            return "failed"
        
        # Make sure image is a valid size
        img_size = os.path.getsize(abs_image_path)
        print(f"Image size: {img_size} bytes")
        
        # Make sure output directory is writable
        output_dir = os.path.dirname(abs_output_path)
        if not os.access(output_dir, os.W_OK):
            print(f"Error: Output directory {output_dir} is not writable")
            return "failed"
        
        # Run the analysis engine
        cmd = ["/usr/local/bin/overflowengine", "--input", abs_image_path, "--output", abs_output_path]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=False,  # Don't raise exception on non-zero exit
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Log the result
        print(f"Command exit code: {result.returncode}")
        if result.stdout:
            print(f"Command stdout: {result.stdout}")
        if result.stderr:
            print(f"Command stderr: {result.stderr}")
        
        # Check if output file was created
        if os.path.exists(abs_output_path):
            with open(abs_output_path, "r") as f:
                result_text = f.read().strip()
            
            print(f"Analysis result text: '{result_text}'")
            
            # Determine result
            if "COVID-19" in result_text:
                print(f"Detected COVID-19")
                return "covid"
            elif "H5N1" in result_text:
                print(f"Detected H5N1")
                return "h5n1"
            elif "healthy" in result_text:
                print(f"Detected healthy sample")
                return "healthy"
            else:
                print(f"Unknown analysis result text: '{result_text}'")
                return "failed"
        else:
            print(f"Error: Output file was not created at {abs_output_path}")
            return "failed"
    
    except Exception as e:
        print(f"Error in process_analysis: {e}")
        import traceback
        traceback.print_exc()
        return "failed"