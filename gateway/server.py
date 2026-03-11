"""
JARVIS — gateway/server.py
FastAPI Gateway server — always-on API that connects all components
Includes token-based auth, rate limiting, and input sanitization
"""

import os
import hmac
import time
import secrets
import yaml
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rich.console import Console

console = Console()

# ─── Request/Response Models ─────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    session_id: int

class MemoryAddRequest(BaseModel):
    text: str | None = None
    file_path: str | None = None

class PlanRequest(BaseModel):
    goal: str

class SkillCreateRequest(BaseModel):
    description: str


# ─── Auth & Rate Limiting ────────────────────

class AuthRateLimiter:
    """Track failed auth attempts per IP — block after threshold."""

    def __init__(self, max_failures: int = 5, window_seconds: int = 60):
        self.max_failures = max_failures
        self.window = window_seconds
        self._failures: dict[str, list[float]] = defaultdict(list)

    def check(self, ip: str) -> bool:
        """Return True if the IP is allowed, False if rate-limited."""
        now = time.time()
        # Clean old entries
        self._failures[ip] = [
            t for t in self._failures[ip] if (now - t) < self.window
        ]
        return len(self._failures[ip]) < self.max_failures

    def record_failure(self, ip: str):
        self._failures[ip].append(time.time())

    def reset(self, ip: str):
        self._failures.pop(ip, None)


rate_limiter = AuthRateLimiter()


def verify_token(request: Request, config: dict) -> bool:
    """
    Verify Bearer token from Authorization header.
    Uses timing-safe comparison (like OpenClaw's secret-equal.ts).
    """
    auth_token = config.get("gateway", {}).get("auth_token", "")
    if not auth_token:
        return True  # No token configured = open access (local mode)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False

    provided = auth_header[7:]  # Strip "Bearer "
    # Timing-safe comparison to prevent timing attacks
    return hmac.compare_digest(provided.encode(), auth_token.encode())


def generate_auth_token(config_path: str = "config.yaml"):
    """Generate and save a random auth token if none exists."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        config = {}

    gateway = config.get("gateway", {})
    if not gateway.get("auth_token"):
        token = secrets.token_urlsafe(32)
        if "gateway" not in config:
            config["gateway"] = {}
        config["gateway"]["auth_token"] = token
        config["gateway"]["host"] = gateway.get("host", "127.0.0.1")
        config["gateway"]["port"] = gateway.get("port", 8000)

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓ Generated gateway auth token[/green]")
        console.print(f"[dim]  Token: {token[:8]}...{token[-4:]}[/dim]")
        console.print(f"[dim]  Stored in: {config_path} → gateway.auth_token[/dim]")
        return token

    return gateway["auth_token"]


# ─── Shared State ────────────────────────────

class JarvisState:
    """Holds all initialized JARVIS components."""
    def __init__(self):
        self.llm = None
        self.rag = None
        self.history = None
        self.router = None
        self.planner = None
        self.skills_loader = None
        self.skill_creator = None
        self.logger = None
        self.config = {}

state = JarvisState()


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def init_components():
    """Initialize all JARVIS components."""
    from brain.llm import JarvisLLM
    from brain.router import Router
    from brain.planner import TaskPlanner
    from memory.rag import RAGMemory
    from memory.history import ConversationHistory
    from memory.indexer import FileIndexer
    from skills.loader import SkillsLoader
    from skills.creator import SkillCreator
    from safety.logger import ActionLogger

    # Generate auth token if needed
    generate_auth_token()

    config = load_config()
    state.config = config
    model_config = config.get("models", {})
    memory_config = config.get("memory", {})

    console.print("[dim]Gateway: Initializing components...[/dim]")

    state.llm = JarvisLLM(
        model=model_config.get("primary", "qwen3.5:2b"),
        host=model_config.get("ollama_host", "http://localhost:11434"),
    )

    state.rag = RAGMemory(
        db_path=memory_config.get("rag_db_path", "./data/rag_db"),
        chunk_size=memory_config.get("chunk_size", 500),
        chunk_overlap=memory_config.get("chunk_overlap", 50),
    )

    state.history = ConversationHistory(
        db_path=memory_config.get("history_db", "./data/history.db"),
    )

    state.router = Router(state.llm)
    state.planner = TaskPlanner(state.llm)

    state.skills_loader = SkillsLoader(skills_dir="skills")
    state.skills_loader.load_all()
    state.skills_loader.start_watcher()

    state.skill_creator = SkillCreator(skills_dir="skills", llm=state.llm)

    state.logger = ActionLogger(
        config.get("safety", {}).get("log_file", "./data/logs/actions.log")
    )

    # Index knowledge directory
    indexer = FileIndexer(state.rag)
    knowledge_dir = memory_config.get("knowledge_dir", "./data/knowledge")
    indexer.index_directory(knowledge_dir)

    console.print("[green]✓ Gateway: All components initialized[/green]")


# ─── App Lifecycle ───────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup, cleanup on shutdown."""
    init_components()
    yield
    if state.history:
        state.history.end_session()
    console.print("[dim]Gateway: Shut down[/dim]")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="JARVIS Gateway",
        description="Local AI assistant API — authenticated",
        version="0.2.0",
        lifespan=lifespan,
    )

    # ─── Auth Middleware ─────────────────────

    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """Authenticate all requests except /status and /docs."""
        # Allow health check and docs without auth
        path = request.url.path
        if path in ("/status", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # Rate limit check
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.check(client_ip):
            state.logger.log("auth_blocked", f"Rate limited: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many failed attempts. Try again later."},
            )

        # Token verification
        if not verify_token(request, state.config):
            rate_limiter.record_failure(client_ip)
            state.logger.log("auth_failed", f"Invalid token from {client_ip}")
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized. Provide valid Bearer token."},
            )

        rate_limiter.reset(client_ip)
        return await call_next(request)

    # ─── Status (no auth) ────────────────────

    @app.get("/status")
    async def get_status():
        """Health check and system status."""
        return {
            "status": "online",
            "model": state.config.get("models", {}).get("primary", "unknown"),
            "memory_documents": state.rag.count() if state.rag else 0,
            "total_messages": state.history.get_total_messages() if state.history else 0,
            "session_id": state.history.session_id if state.history else None,
            "skills_loaded": len(state.skills_loader.skills) if state.skills_loader else 0,
            "auth_enabled": bool(state.config.get("gateway", {}).get("auth_token")),
        }

    # ─── Chat ────────────────────────────────

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Send a message and get a response."""
        from safety.sanitize import sanitize_input, check_injection

        user_msg = sanitize_input(request.message)

        if not user_msg:
            raise HTTPException(status_code=400, detail="Empty message")

        # Log injection attempts (don't block — just log)
        if check_injection(user_msg):
            state.logger.log("injection_attempt", f"Suspicious input: {user_msg[:100]}")

        # Classify intent
        intent = state.router.classify(user_msg)
        state.logger.log("route", f"Intent: {intent} | Input: {user_msg[:100]}")

        # Check skills first
        skill = state.skills_loader.find_skill(user_msg) if state.skills_loader else None
        if skill:
            result = state.skills_loader.execute_skill(skill.name, user_msg)
            state.history.save_message("user", user_msg)
            state.history.save_message("assistant", result)
            state.logger.log("skill", f"Executed: {skill.name}")
            return ChatResponse(
                response=result,
                intent="skill",
                session_id=state.history.session_id,
            )

        # RAG-augmented chat
        state.history.save_message("user", user_msg)
        conversation = state.history.get_recent(10)
        if conversation:
            conversation = conversation[:-1]

        rag_context = state.rag.get_context(user_msg) if state.rag else ""

        system_prompt = state.llm.SYSTEM_PROMPT
        if rag_context:
            system_prompt += (
                f"\n\nRelevant context from the user's documents:\n"
                f"---\n{rag_context}\n---\n"
                f"Use this context when relevant."
            )

        response = state.llm.chat(user_msg, conversation=conversation, system_prompt=system_prompt)
        state.history.save_message("assistant", response)
        state.logger.log("llm_chat", f"Query: {user_msg[:80]}")

        return ChatResponse(
            response=response,
            intent=intent,
            session_id=state.history.session_id,
        )

    # ─── Memory ──────────────────────────────

    @app.post("/memory/add")
    async def add_memory(request: MemoryAddRequest):
        """Add text or a document to RAG memory."""
        if request.text:
            state.rag.add_text(request.text, source="api_input")
            return {"status": "ok", "message": "Text added to memory"}
        elif request.file_path:
            # Validate file path exists and is readable
            if not os.path.isfile(request.file_path):
                raise HTTPException(status_code=400, detail="File not found")
            state.rag.add_document(request.file_path)
            return {"status": "ok", "message": f"Document added: {request.file_path}"}
        return JSONResponse(status_code=400, content={"error": "Provide text or file_path"})

    @app.get("/memory/search")
    async def search_memory(query: str, top_k: int = 3):
        """Search RAG memory."""
        results = state.rag.query(query, top_k=min(top_k, 10))  # Cap at 10
        return {"query": query, "results": results}

    @app.get("/memory/stats")
    async def memory_stats():
        """Get memory statistics."""
        return {
            "rag_documents": state.rag.count() if state.rag else 0,
            "total_messages": state.history.get_total_messages() if state.history else 0,
            "current_session": state.history.session_id if state.history else None,
        }

    # ─── Plan ────────────────────────────────

    @app.post("/plan")
    async def create_plan(request: PlanRequest):
        """Break a goal into executable steps."""
        steps = state.planner.decompose(request.goal)
        state.logger.log("plan", f"Goal: {request.goal[:80]}")
        return {"goal": request.goal, "steps": steps}

    # ─── Skills ──────────────────────────────

    @app.get("/skills")
    async def list_skills():
        """List all loaded skills."""
        return {
            "skills": state.skills_loader.list_skills() if state.skills_loader else [],
        }

    @app.post("/skills/create")
    async def create_skill(request: SkillCreateRequest):
        """Create a new skill using LLM."""
        filepath = state.skill_creator.create_from_llm(request.description)
        return {"status": "ok", "filepath": filepath}

    @app.post("/skills/execute/{skill_name}")
    async def execute_skill(skill_name: str, request: ChatRequest):
        """Execute a specific skill."""
        result = state.skills_loader.execute_skill(skill_name, request.message)
        return {"skill": skill_name, "result": result}

    # ─── WebSocket (Streaming Chat) ──────────

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for streaming chat responses."""
        await websocket.accept()

        try:
            while True:
                data = await websocket.receive_text()

                state.history.save_message("user", data)
                conversation = state.history.get_recent(10)
                if conversation:
                    conversation = conversation[:-1]

                rag_context = state.rag.get_context(data) if state.rag else ""
                system_prompt = state.llm.SYSTEM_PROMPT
                if rag_context:
                    system_prompt += f"\n\nContext:\n{rag_context}"

                full_response = ""
                for chunk in state.llm.stream_chat(data, conversation=conversation, system_prompt=system_prompt):
                    await websocket.send_text(chunk)
                    full_response += chunk

                await websocket.send_text("[DONE]")
                state.history.save_message("assistant", full_response)

        except WebSocketDisconnect:
            pass

    return app


# Create the app instance for uvicorn
app = create_app()
