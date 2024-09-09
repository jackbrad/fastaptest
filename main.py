from fastapi import FastAPI
import subprocess

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/generate")
async def generate_diagram():
    cmd = "docker run --rm -u 0:0 -v /path/to/diagrams:/data minlag/mermaid-cli -i diagram.mmd -o output-diagram.png"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}
