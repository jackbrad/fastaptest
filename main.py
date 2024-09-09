
import boto3
from fastapi import FastAPI, HTTPException
import subprocess
import os

app = FastAPI()
s3 = boto3.client('s3')

@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/generate")
async def generate_diagram():
    cmd = "docker run --rm -u 0:0 -v /home/ec2-user/mmd_examples/data:/data minlag/mermaid-cli -i diagram.mmd -o output-diagram.png"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}



