@app.get("/generate")
async def generate_diagram(input_file: str):
    # Parse the S3 URL
    parsed_url = urlparse(input_file)
    bucket = parsed_url.netloc.split('.')[0]
    s3_key = parsed_url.path.lstrip('/')

    # Generate output filename
    output_file = os.path.basename(s3_key).rsplit('.', 1)[0] + '.png'
    output_s3_key = os.path.join(os.path.dirname(s3_key), output_file)
    
    # Set full paths for input and output files
    input_path = os.path.join(TEMP_DIR, os.path.basename(s3_key))
    output_path = os.path.join(TEMP_DIR, output_file)
    
    # Download file from S3
    s3.download_file(bucket, s3_key, input_path)
    
    # Generate diagram
    cmd = f"docker run --rm -u 0:0 -v {TEMP_DIR}:/data minlag/mermaid-cli -i {os.path.basename(s3_key)} -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)
    
    # Upload generated image back to S3
    s3.upload_file(output_path, bucket, output_s3_key)
    
    # Clean up temporary files
    os.remove(input_path)
    os.remove(output_path)
    
    # Return the S3 URL of the uploaded file
    return {"message": "Diagram generated and uploaded", "url": f"https://{bucket}.s3.amazonaws.com/{output_s3_key}"}
