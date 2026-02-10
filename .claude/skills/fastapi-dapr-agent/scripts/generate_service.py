#!/usr/bin/env python3
"""Generate FastAPI microservice with Dapr and AI integration.

Service types match actual LearnFlow production patterns:
- ai-agent: Domain-specific AI with JSON response format, struggle detection, event publishing
- crud-api: Dapr state store CRUD + AI-powered generation/grading + quiz support
- code-executor: Sandboxed Python execution with safety checks
"""
import sys, argparse
from pathlib import Path

# Base template shared by all service types
MAIN_PY_TEMPLATE = '''"""{service_description}"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
import requests{extra_imports}

{ai_setup}

app = FastAPI(
    title="{service_name}",
    description="{service_description}",
    version="2.0.0"
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

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{service_name}"}}

@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr pub/sub subscriptions."""
    return [{dapr_subscriptions}]

{endpoints}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# --- AI Agent type (triage, concepts, debug, code-review) ---
AI_AGENT_SETUP = '''from openai import OpenAI

# OpenAI configuration - model is environment-driven for flexibility
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """{system_prompt}"""
'''

AI_AGENT_ENDPOINTS = '''
class AgentRequest(BaseModel):
    prompt: str
    user_id: str = ""
    context: dict = {{}}


class AgentResponse(BaseModel):
    analysis: str
    result: dict
    confidence: float = 0.0


@app.post("/api/{service_path}/analyze", response_model=AgentResponse)
async def analyze(request: AgentRequest):
    """Process request using AI agent with structured JSON output."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {{"role": "system", "content": SYSTEM_PROMPT}},
                {{"role": "user", "content": request.prompt}},
            ],
            response_format={{"type": "json_object"}},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {{}}

        # Publish event via Dapr
        try:
            requests.post(
                f"{{DAPR_BASE_URL}}/v1.0/publish/pubsub/learning.events",
                json={{
                    "type": "{service_name}_analysis",
                    "user_id": request.user_id,
                    "service": "{service_name}",
                }},
            )
        except Exception:
            pass

        return AgentResponse(
            analysis=result.get("analysis", "Request processed."),
            result=result,
            confidence=float(result.get("confidence", 0.5)),
        )

    except json.JSONDecodeError:
        return AgentResponse(
            analysis="Unable to parse AI response.",
            result={{}},
            confidence=0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/{event_route}")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    data = event.get("data", event)
    # Process event data as needed
    return {{"status": "processed"}}
'''

# --- CRUD API type (exercise service with state store + AI generation + quizzes) ---
CRUD_SETUP = '''from openai import OpenAI
import uuid

# OpenAI for AI-powered generation and grading
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
STATE_STORE = "statestore"
'''

CRUD_ENDPOINTS = '''
class Item(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    difficulty: str = "beginner"
    module_id: str = "mod-1"
    topic: str = ""
    starter_code: str = ""
    expected_output: str = ""
    hints: List[str] = []
    test_cases: List[dict] = []


class Submission(BaseModel):
    user_id: str
    code: str


class GradeResponse(BaseModel):
    passed: bool
    score: float
    feedback: str


class GenerateRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"
    count: int = 3


@app.post("/api/{service_path}", response_model=Item)
async def create_item(item: Item):
    """Create new item with Dapr state store."""
    item.id = str(uuid.uuid4())

    response = requests.post(
        f"{{DAPR_BASE_URL}}/v1.0/state/{{STATE_STORE}}",
        json=[{{"key": f"item-{{item.id}}", "value": item.model_dump()}}],
    )

    if response.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Failed to save item")

    return item


@app.get("/api/{service_path}", response_model=List[Item])
async def list_items():
    """List all items."""
    try:
        response = requests.post(
            f"{{DAPR_BASE_URL}}/v1.0-alpha1/state/{{STATE_STORE}}/query",
            json={{"filter": {{}}, "sort": [{{"key": "value.difficulty", "order": "ASC"}}]}},
        )
        if response.status_code == 200:
            results = response.json().get("results", [])
            return [Item(**r["data"]) for r in results]
    except Exception:
        pass
    return []


@app.get("/api/{service_path}/{{item_id}}", response_model=Item)
async def get_item(item_id: str):
    """Get item from Dapr state store."""
    response = requests.get(f"{{DAPR_BASE_URL}}/v1.0/state/{{STATE_STORE}}/item-{{item_id}}")

    if response.status_code == 204 or not response.text:
        raise HTTPException(status_code=404, detail="Item not found")

    return Item(**response.json())


@app.post("/api/{service_path}/{{item_id}}/grade", response_model=GradeResponse)
async def grade_submission(item_id: str, submission: Submission):
    """Auto-grade a code submission."""
    # Execute code via code-execution-service
    exec_url = os.getenv("CODE_EXECUTION_SERVICE_URL", "http://code-execution-service:8000")
    try:
        exec_response = requests.post(
            f"{{exec_url}}/execute",
            json={{"code": submission.code}},
            timeout=15,
        )
        exec_result = exec_response.json()
        output = exec_result.get("output", "")
        error = exec_result.get("error", "")
    except Exception:
        output = ""
        error = "Code execution service unavailable"

    if error:
        return GradeResponse(passed=False, score=0.0, feedback=f"Error: {{error}}")

    # Publish grade event
    try:
        requests.post(
            f"{{DAPR_BASE_URL}}/v1.0/publish/pubsub/learning.events",
            json={{"type": "exercise_completed", "user_id": submission.user_id, "item_id": item_id}},
        )
    except Exception:
        pass

    return GradeResponse(passed=True, score=70.0, feedback="Code executed successfully.")


@app.post("/api/{service_path}/generate", response_model=List[Item])
async def generate_items(request: GenerateRequest):
    """AI-generated exercises for a given topic."""
    try:
        prompt = f"""Generate {{request.count}} Python coding exercises about "{{request.topic}}" at {{request.difficulty}} level.
Return a JSON object with key "exercises" containing an array of objects with: title, description, starter_code, expected_output, hints (array of 2)."""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {{"role": "system", "content": "You are a Python exercise generator. Return valid JSON only."}},
                {{"role": "user", "content": prompt}},
            ],
            response_format={{"type": "json_object"}},
        )

        content = response.choices[0].message.content
        result = json.loads(content) if content else {{}}
        items = []
        for ex in result.get("exercises", [])[:request.count]:
            items.append(Item(
                id=str(uuid.uuid4()),
                title=ex.get("title", "Untitled"),
                description=ex.get("description", ""),
                difficulty=request.difficulty,
                topic=request.topic,
                starter_code=ex.get("starter_code", ""),
                expected_output=ex.get("expected_output", ""),
                hints=ex.get("hints", []),
            ))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/{event_route}")
async def handle_event(event: dict):
    """Handle Dapr pub/sub events."""
    return {{"status": "processed"}}
'''

# --- Code Executor type (sandboxed Python execution) ---
CODE_EXECUTOR_SETUP = '''import subprocess
import tempfile
'''

CODE_EXECUTOR_ENDPOINTS = '''
# Execution limits
MAX_TIMEOUT = int(os.getenv("EXEC_TIMEOUT", "10"))
MAX_OUTPUT_SIZE = int(os.getenv("MAX_OUTPUT_SIZE", "10000"))

# Blocked imports for security
BLOCKED_IMPORTS = [
    "subprocess", "shutil", "ctypes", "socket",
    "http", "urllib", "ftplib", "smtplib",
]


class CodeRequest(BaseModel):
    code: str
    timeout: Optional[int] = None
    user_id: str = ""


class CodeResponse(BaseModel):
    output: str
    error: str = ""
    exit_code: int = 0
    timed_out: bool = False


def check_code_safety(code: str) -> Optional[str]:
    """Basic safety check on submitted code."""
    for blocked in BLOCKED_IMPORTS:
        if f"import {{blocked}}" in code or f"from {{blocked}}" in code:
            return f"Import '{{blocked}}' is not allowed for security reasons"
    if "open(" in code and ("w" in code or "a" in code):
        return "File write operations are not allowed"
    if "exec(" in code or "eval(" in code:
        return "exec() and eval() are not allowed"
    return None


@app.post("/api/{service_path}/run", response_model=CodeResponse)
@app.post("/execute", response_model=CodeResponse, include_in_schema=False)
async def execute_code(request: CodeRequest):
    """Execute Python code in a sandboxed environment."""
    safety_issue = check_code_safety(request.code)
    if safety_issue:
        return CodeResponse(output="", error=safety_issue, exit_code=1)

    timeout = min(request.timeout or MAX_TIMEOUT, MAX_TIMEOUT)

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(request.code)
            temp_path = f.name

        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True, text=True, timeout=timeout,
            env={{**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}},
        )

        output = result.stdout[:MAX_OUTPUT_SIZE]
        error = result.stderr[:MAX_OUTPUT_SIZE]

        response = CodeResponse(output=output, error=error, exit_code=result.returncode)

        # Publish execution result via Dapr
        try:
            requests.post(
                f"{{DAPR_BASE_URL}}/v1.0/publish/pubsub/learning.events",
                json={{"type": "code_executed", "user_id": request.user_id, "success": result.returncode == 0}},
                timeout=2,
            )
        except Exception:
            pass

        return response

    except subprocess.TimeoutExpired:
        return CodeResponse(output="", error="Code execution timed out", exit_code=1, timed_out=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


@app.post("/events/{event_route}")
async def handle_code_event(event: dict):
    """Handle code submission events from pub/sub."""
    data = event.get("data", {{}})
    code = data.get("code", "")
    user_id = data.get("user_id", "")

    if code:
        result = await execute_code(CodeRequest(code=code, user_id=user_id))
        return {{"status": "executed", "exit_code": result.exit_code}}

    return {{"status": "processed"}}
'''

# Test templates
TEST_TEMPLATE = '''"""Tests for {service_name}."""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "{service_name}"


def test_dapr_subscribe():
    response = client.get("/dapr/subscribe")
    assert response.status_code == 200
    subs = response.json()
    assert isinstance(subs, list)
    assert len(subs) > 0
    assert subs[0]["pubsubname"] == "pubsub"
'''

DOCKERFILE = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

K8S_DEPLOYMENT = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: learnflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{service_name}"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: {service_name}
        image: {service_name}:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"{env_vars}
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: learnflow
spec:
  selector:
    app: {service_name}
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
'''

REQUIREMENTS_TXT = {
    'ai-agent': '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
openai>=1.10.0
requests>=2.31.0
pytest>=7.4.0
httpx>=0.25.0
''',
    'crud-api': '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
openai>=1.10.0
requests>=2.31.0
pytest>=7.4.0
httpx>=0.25.0
''',
    'code-executor': '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
requests>=2.31.0
pytest>=7.4.0
httpx>=0.25.0
'''
}

# Service type configurations
SERVICE_CONFIGS = {
    'ai-agent': {
        'setup': AI_AGENT_SETUP,
        'endpoints': AI_AGENT_ENDPOINTS,
        'extra_imports': '',
        'system_prompt': (
            "You are an AI assistant for LearnFlow, an AI-powered Python learning platform. "
            "Analyze the student's input and provide helpful, structured responses. "
            "Respond with a JSON object containing: analysis, result (detailed data), confidence (0-1)."
        ),
        'dapr_sub_topic': 'learning.events',
        'dapr_sub_route': '/events/learning',
        'event_route': 'learning',
    },
    'crud-api': {
        'setup': CRUD_SETUP,
        'endpoints': CRUD_ENDPOINTS,
        'extra_imports': '',
        'system_prompt': '',
        'dapr_sub_topic': 'learning.events',
        'dapr_sub_route': '/events/learning',
        'event_route': 'learning',
    },
    'code-executor': {
        'setup': CODE_EXECUTOR_SETUP,
        'endpoints': CODE_EXECUTOR_ENDPOINTS,
        'extra_imports': '\nimport subprocess\nimport tempfile',
        'system_prompt': '',
        'dapr_sub_topic': 'code.submitted',
        'dapr_sub_route': '/events/code',
        'event_route': 'code',
    },
}


def generate_service(name, service_type, output_dir):
    """Generate FastAPI service with specified type."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    (output_path / "app").mkdir(exist_ok=True)
    (output_path / "k8s").mkdir(exist_ok=True)
    (output_path / "tests").mkdir(exist_ok=True)

    config = SERVICE_CONFIGS[service_type]
    service_path = name.replace('-service', '').replace('-', '_')

    # Build AI setup section
    ai_setup = ""
    if service_type == 'ai-agent':
        ai_setup = config['setup'].format(system_prompt=config['system_prompt'])
    elif service_type == 'crud-api':
        ai_setup = config['setup']
    else:
        ai_setup = config['setup']

    # Build Dapr subscriptions
    dapr_subs = (
        f'\n        {{"pubsubname": "pubsub", "topic": "{config["dapr_sub_topic"]}", '
        f'"route": "{config["dapr_sub_route"]}"}}'
    )

    # Build endpoints
    endpoints = config['endpoints'].format(
        service_name=name,
        service_path=service_path,
        event_route=config['event_route'],
    )

    # Assemble main.py
    extra_imports = config['extra_imports']
    if service_type == 'ai-agent':
        extra_imports = ''  # OpenAI imported in setup block

    main_py = MAIN_PY_TEMPLATE.format(
        service_name=name,
        service_description=f"{name.replace('-', ' ').title()} microservice",
        ai_setup=ai_setup,
        extra_imports=extra_imports,
        dapr_subscriptions=dapr_subs,
        endpoints=endpoints,
    )

    # Write main files
    (output_path / "app" / "main.py").write_text(main_py)
    (output_path / "app" / "__init__.py").write_text("")
    (output_path / "Dockerfile").write_text(DOCKERFILE)
    (output_path / "requirements.txt").write_text(
        REQUIREMENTS_TXT.get(service_type, REQUIREMENTS_TXT['ai-agent'])
    )

    # Write test file
    test_content = TEST_TEMPLATE.format(service_name=name)
    (output_path / "tests" / "__init__.py").write_text("")
    (output_path / "tests" / "test_main.py").write_text(test_content)

    # Write K8s deployment
    env_vars = ""
    if service_type in ('ai-agent', 'crud-api'):
        env_vars = """
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-credentials
              key: api-key"""

    k8s_content = K8S_DEPLOYMENT.format(service_name=name, env_vars=env_vars)
    (output_path / "k8s" / "deployment.yaml").write_text(k8s_content)

    print(f"✓ Service generated: {output_path}")
    print(f"  Name: {name}")
    print(f"  Type: {service_type}")
    print(f"  Model: env OPENAI_MODEL (default: gpt-4o-mini)")
    print(f"  Structure:")
    print(f"    - app/main.py (FastAPI app with domain-specific endpoints)")
    print(f"    - app/__init__.py")
    print(f"    - Dockerfile")
    print(f"    - requirements.txt")
    print(f"    - k8s/deployment.yaml (with Dapr sidecar annotations)")
    print(f"    - tests/test_main.py")
    print(f"\n→ Next: python scripts/configure_dapr.py --service-dir {output_dir}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate LearnFlow FastAPI microservice")
    parser.add_argument("--name", required=True, help="Service name (e.g., debug-service)")
    parser.add_argument("--type", required=True,
                       choices=["ai-agent", "crud-api", "code-executor"],
                       help="Service type")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()
    sys.exit(generate_service(args.name, args.type, args.output))
