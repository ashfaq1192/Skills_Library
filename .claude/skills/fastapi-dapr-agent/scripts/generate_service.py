#!/usr/bin/env python3
"""Generate FastAPI microservice with Dapr and AI integration."""
import sys, argparse
from pathlib import Path

# FastAPI main.py template
MAIN_PY_TEMPLATE = '''"""FastAPI application with Dapr integration."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os{ai_imports}

app = FastAPI(
    title="{service_name}",
    description="{service_description}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{{DAPR_HTTP_PORT}}"
{ai_config}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{service_name}"}}

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [
        {{"pubsubname": "pubsub", "topic": "{service_topic}", "route": "/events"}}
    ]

{endpoints}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# AI Agent endpoints
AI_AGENT_ENDPOINTS = '''
# OpenAI configuration
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AgentRequest(BaseModel):
    prompt: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    tokens_used: int

@app.post("/process", response_model=AgentResponse)
async def process_request(request: AgentRequest):
    """Process request using AI agent."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for {service_name}."},
                {"role": "user", "content": request.prompt}
            ]
        )

        return AgentResponse(
            response=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    # Process event with AI if needed
    return {"status": "processed"}
'''

CRUD_ENDPOINTS = '''
from typing import List, Optional

class Item(BaseModel):
    id: Optional[str] = None
    name: str
    data: dict = {}

@app.post("/items")
async def create_item(item: Item):
    """Create new item with Dapr state store."""
    import requests
    import uuid

    item_id = str(uuid.uuid4())
    item.id = item_id

    # Save to Dapr state store
    response = requests.post(
        f"{DAPR_BASE_URL}/v1.0/state/statestore",
        json=[{"key": item_id, "value": item.dict()}]
    )

    if response.status_code != 204:
        raise HTTPException(status_code=500, detail="Failed to save item")

    return item

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get item from Dapr state store."""
    import requests

    response = requests.get(f"{DAPR_BASE_URL}/v1.0/state/statestore/{item_id}")

    if response.status_code == 204:
        raise HTTPException(status_code=404, detail="Item not found")

    return response.json()

@app.post("/events")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    return {"status": "processed"}
'''

DOCKERFILE = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

REQUIREMENTS_TXT = {
    'ai-agent': '''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
openai==1.10.0
requests==2.31.0
''',
    'crud-api': '''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
requests==2.31.0
''',
    'event-processor': '''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
requests==2.31.0
''',
    'code-executor': '''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
requests==2.31.0
'''
}

def generate_service(name, service_type, output_dir):
    """Generate FastAPI service with specified type."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    (output_path / "app").mkdir(exist_ok=True)
    (output_path / "k8s").mkdir(exist_ok=True)
    (output_path / "tests").mkdir(exist_ok=True)

    # Generate main.py based on type
    ai_imports = ""
    ai_config = ""

    if service_type == "ai-agent":
        endpoints = AI_AGENT_ENDPOINTS
        ai_imports = "\\nfrom openai import OpenAI"
        ai_config = 'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")'
    elif service_type == "crud-api":
        endpoints = CRUD_ENDPOINTS
    else:
        endpoints = CRUD_ENDPOINTS

    main_py = MAIN_PY_TEMPLATE.format(
        service_name=name,
        service_description=f"{name.replace('-', ' ').title()} microservice",
        service_topic=name.replace('-', '_'),
        ai_imports=ai_imports,
        ai_config=ai_config,
        endpoints=endpoints
    )

    # Write files
    (output_path / "app" / "main.py").write_text(main_py)
    (output_path / "app" / "__init__.py").write_text("")
    (output_path / "Dockerfile").write_text(DOCKERFILE)
    (output_path / "requirements.txt").write_text(REQUIREMENTS_TXT.get(service_type, REQUIREMENTS_TXT['crud-api']))
    (output_path / "tests" / "__init__.py").write_text("")

    print(f"✓ Service generated: {output_path}")
    print(f"  Name: {name}")
    print(f"  Type: {service_type}")
    print(f"  Structure:")
    print(f"    - app/main.py (FastAPI app)")
    print(f"    - Dockerfile")
    print(f"    - requirements.txt")
    print(f"    - k8s/ (manifests)")
    print(f"    - tests/")
    print(f"\\n→ Next: python scripts/configure_dapr.py --service-dir {output_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Service name")
    parser.add_argument("--type", required=True,
                       choices=["ai-agent", "crud-api", "event-processor", "code-executor"],
                       help="Service type")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()
    sys.exit(generate_service(args.name, args.type, args.output))
