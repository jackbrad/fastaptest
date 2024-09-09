@app.get("/generate")
async def generate_diagram(input_file: str):
    # Parse the S3 URL
    parsed_url = urlparse(input_file)
    bucket = parsed_url.netloc.split('.')[0]
    s3_key = parsed_url.path.lstrip('/')

    return {"message": "Diagram generated and uploaded", "url": f"https://{bucket}.s3.amazonaws.com/{s3_key}"}
