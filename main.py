
import boto3
from fastapi import FastAPI, HTTPException
import subprocess
import os

app = FastAPI()
s3 = boto3.client('s3')
TEMP_DIR = '/home/ec2-user/mmd_examples/data'


@app.get("/test")
def root():
    return {"Hello": "World"}



@app.get("/generate")
async def generate_diagram(input_file: str, bucket: str):
    # Generate output filename
    output_file = os.path.splitext(input_file)[0] + '.png'
    
    # Set full paths for input and output files
    input_path = os.path.join(TEMP_DIR, input_file)
    output_path = os.path.join(TEMP_DIR, output_file)
    
    # Download file from S3
    s3.download_file(bucket, input_file, input_path)
    
    # Generate diagram
    cmd = f"docker run --rm -u 0:0 -v {TEMP_DIR}:/data minlag/mermaid-cli -i {input_file} -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)
    
    # Upload generated image back to S3
    s3.upload_file(output_path, bucket, output_file)
    
    # Clean up temporary files
    os.remove(input_path)
    os.remove(output_path)
    
    # Return the S3 URL of the uploaded file
    return {"message": "Diagram generated and uploaded", "url": f"s3://{bucket}/{output_file}"}
