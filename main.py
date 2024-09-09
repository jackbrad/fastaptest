import boto3
from fastapi import FastAPI, HTTPException
import subprocess
import os
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
s3 = boto3.client('s3')

TEMP_DIR = '/home/ec2-user/mmd_examples/data'

@app.get("/test")
def test_api():
    logger.info("Test API endpoint called")
    return {"status": "ok", "message": "API is running"}

@app.get("/generate")
def generate_diagram(input_file: str):
    logger.info(f"Received request to generate diagram for: {input_file}")

    # Parse the S3 URL
    parsed_url = urlparse(input_file)
    bucket = parsed_url.netloc.split('.')[0]
    s3_key = parsed_url.path.lstrip('/')
    logger.info(f"Parsed S3 URL - Bucket: {bucket}, Key: {s3_key}")

    # Generate output filename
    output_file = os.path.basename(s3_key).rsplit('.', 1)[0] + '.png'
    output_s3_key = os.path.join(os.path.dirname(s3_key), output_file)
    logger.info(f"Generated output filename: {output_file}, S3 key: {output_s3_key}")
    
    # Set full paths for input and output files
    input_path = os.path.join(TEMP_DIR, os.path.basename(s3_key))
    output_path = os.path.join(TEMP_DIR, output_file)
    logger.info(f"Local file paths - Input: {input_path}, Output: {output_path}")
    
    try:
        # Download file from S3
        logger.info(f"Downloading file from S3: {s3_key}")
        s3.download_file(bucket, s3_key, input_path)
        logger.info("File downloaded successfully")
        
        # Generate diagram
        cmd = f"docker run --rm -u 0:0 -v {TEMP_DIR}:/data minlag/mermaid-cli -i {os.path.basename(s3_key)} -o {output_file}"
        logger.info(f"Executing command: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"Subprocess output: {result.stdout}")
        
        # Check if output file was created
        if os.path.exists(output_path):
            logger.info(f"Output file created successfully: {output_path}")
        else:
            logger.error(f"Output file was not created: {output_path}")
            raise HTTPException(status_code=500, detail="Output file was not created")
        
        # Upload generated image back to S3
        logger.info(f"Uploading file to S3: {output_s3_key}")
        s3.upload_file(output_path, bucket, output_s3_key)
        logger.info("File uploaded successfully")
        
        # Clean up temporary files
        logger.info("Cleaning up temporary files")
        os.remove(input_path)
        os.remove(output_path)
        logger.info("Temporary files removed")
        
        # Return the S3 URL of the uploaded file
        result_url = f"https://{bucket}.s3.amazonaws.com/{output_s3_key}"
        logger.info(f"Operation completed successfully. Result URL: {result_url}")
        return {"message": "Diagram generated and uploaded", "url": result_url}
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
