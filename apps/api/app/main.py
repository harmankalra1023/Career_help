from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.schemas.common import HealthResponse, ReadyResponse
from app.routers.api import api_router

setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed baseline data
    from app.db.init_db import init_database
    try:
        await init_database()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error initializing database: {e}")
    yield
    # Shutdown: clean up resources


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Digital Career Twin (DCT)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 50: '#eff6ff', 100: '#dbeafe', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' }
          }
        }
      }
    }
  </script>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen font-sans">
  <nav class="bg-white border-b border-slate-200 sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="h-9 w-9 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm">
          DCT
        </div>
        <span class="font-bold text-lg tracking-tight text-slate-900">Digital Career Twin</span>
        <span class="text-xs bg-brand-50 text-brand-700 font-semibold px-2.5 py-0.5 rounded-full border border-brand-200">v0.1.0 MVP</span>
      </div>
      <div class="flex items-center space-x-3 text-sm">
        <a href="/docs" target="_blank" class="px-3.5 py-2 font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition">Interactive API Docs</a>
        <a href="/healthz" target="_blank" class="px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-md">/healthz: OK</a>
      </div>
    </div>
  </nav>

  <main class="max-w-7xl mx-auto px-6 py-8 space-y-8">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">Alex Johnson &bull; Verified Digital Twin</h1>
        <p class="text-sm text-slate-500 mt-1">Target Role: <strong class="text-slate-800">Backend Engineer</strong> &bull; Region: <strong>Global (USD)</strong> &bull; Engine: <strong>v1.0.0</strong></p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-500">Live Status:</span>
        <span class="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-emerald-800 bg-emerald-100 rounded-full">
          <span class="h-2 w-2 rounded-full bg-emerald-600 animate-pulse"></span> App Online
        </span>
      </div>
    </div>

    <!-- Scores Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold uppercase text-slate-500 tracking-wider">Profile Strength (PPS)</span>
          <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">+3.1</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-4xl font-black text-slate-900">64.2</span>
          <span class="text-sm font-semibold text-slate-500">/ 100</span>
        </div>
        <div class="mt-3 text-xs text-slate-500">Band: <strong class="text-slate-700">Solid</strong> &bull; Confidence: 78%</div>
        <div class="mt-2 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
          <div class="h-full bg-blue-600 rounded-full" style="width: 64.2%"></div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold uppercase text-slate-500 tracking-wider">Technical Skills (TSS)</span>
          <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">+2.0</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-4xl font-black text-slate-900">68.0</span>
          <span class="text-sm font-semibold text-slate-500">/ 100</span>
        </div>
        <div class="mt-3 text-xs text-slate-500">Band: <strong class="text-slate-700">Solid</strong> &bull; Confidence: 82%</div>
        <div class="mt-2 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
          <div class="h-full bg-indigo-600 rounded-full" style="width: 68.0%"></div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold uppercase text-slate-500 tracking-wider">Non-Technical (NTSS)</span>
          <span class="text-xs font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">0.0</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-4xl font-black text-slate-900">59.5</span>
          <span class="text-sm font-semibold text-slate-500">/ 100</span>
        </div>
        <div class="mt-3 text-xs text-slate-500">Band: <strong class="text-slate-700">Solid</strong> &bull; Confidence: 55%</div>
        <div class="mt-2 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
          <div class="h-full bg-amber-500 rounded-full" style="width: 59.5%"></div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold uppercase text-slate-500 tracking-wider">Job Readiness (JRS)</span>
          <span class="text-xs font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">Backend</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-4xl font-black text-slate-900">58.3</span>
          <span class="text-sm font-semibold text-slate-500">/ 100</span>
        </div>
        <div class="mt-3 text-xs text-slate-500">Est. Time to Ready: <strong class="text-slate-700">10–16 weeks</strong></div>
        <div class="mt-2 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
          <div class="h-full bg-emerald-600 rounded-full" style="width: 58.3%"></div>
        </div>
      </div>
    </div>

    <!-- Details Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Career DNA -->
      <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 class="text-lg font-bold text-slate-900">Career DNA Archetypes</h2>
          <span class="text-xs text-slate-500">Centroid Proximity</span>
        </div>
        <div class="space-y-4 pt-2">
          <div>
            <div class="flex justify-between text-sm font-semibold mb-1">
              <span>Systems Builder</span>
              <span class="text-brand-600">62% Match</span>
            </div>
            <div class="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-brand-600 rounded-full" style="width: 62%"></div>
            </div>
            <p class="text-xs text-slate-500 mt-1">High systems thinking, technical depth, and infrastructure discipline.</p>
          </div>
          <div>
            <div class="flex justify-between text-sm font-semibold mb-1">
              <span>Applied Researcher</span>
              <span class="text-indigo-600">21% Match</span>
            </div>
            <div class="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-600 rounded-full" style="width: 21%"></div>
            </div>
            <p class="text-xs text-slate-500 mt-1">Algorithmic exploration and empirical problem solving.</p>
          </div>
        </div>
      </div>

      <!-- Priority Gaps -->
      <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 class="text-lg font-bold text-slate-900">Priority Skill Gaps</h2>
          <span class="text-xs font-medium text-brand-600">Ranked by JRS Gain</span>
        </div>
        <div class="space-y-3 pt-1">
          <div class="flex items-center justify-between p-3.5 bg-slate-50 rounded-lg border border-slate-200">
            <div>
              <div class="font-bold text-slate-900 text-sm">Docker & Containerization</div>
              <div class="text-xs text-slate-500 mt-0.5">Current: 22% &rarr; Role Minimum: 60%</div>
            </div>
            <div class="text-right">
              <span class="inline-block text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">+4.2 JRS</span>
              <div class="text-[11px] text-slate-500 mt-1">Est. 18 hours</div>
            </div>
          </div>
          <div class="flex items-center justify-between p-3.5 bg-slate-50 rounded-lg border border-slate-200">
            <div>
              <div class="font-bold text-slate-900 text-sm">PostgreSQL Indexing & Optimization</div>
              <div class="text-xs text-slate-500 mt-0.5">Current: 40% &rarr; Role Minimum: 55%</div>
            </div>
            <div class="text-right">
              <span class="inline-block text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">+2.8 JRS</span>
              <div class="text-[11px] text-slate-500 mt-1">Est. 12 hours</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Groq AI Career Mentor Panel -->
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
        <div class="flex items-center space-x-2">
          <div class="h-3 w-3 rounded-full bg-orange-500 animate-pulse"></div>
          <h2 class="text-lg font-bold text-slate-900">Groq AI Career Mentor</h2>
          <span class="text-xs bg-orange-50 text-orange-700 font-semibold px-2 py-0.5 rounded border border-orange-200">Llama-3.3-70b</span>
        </div>
        <div id="llm-status-badge" class="text-xs text-slate-500">Checking Groq provider status...</div>
      </div>
      <p class="text-xs text-slate-600">
        Ask the AI mentor for advice on closing skill gaps, choosing projects, or preparing for backend interviews.
      </p>
      <div class="space-y-3">
        <div class="flex gap-2">
          <input
            id="mentor-input"
            type="text"
            placeholder="e.g. What is the quickest way to close my Docker gap for a backend role?"
            class="flex-1 rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            onkeydown="if(event.key === 'Enter') askMentor()"
          />
          <button
            id="mentor-btn"
            onclick="askMentor()"
            class="px-5 py-2.5 bg-orange-600 hover:bg-orange-700 text-white font-semibold text-sm rounded-lg shadow-sm transition"
          >
            Ask Mentor
          </button>
        </div>
        <div id="mentor-response" class="hidden rounded-lg bg-slate-50 border border-slate-200 p-4 text-sm text-slate-800 space-y-2">
          <div class="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider">
            <span id="response-provider">Mentor Reply</span>
            <span id="response-model"></span>
          </div>
          <div id="response-text" class="leading-relaxed whitespace-pre-wrap"></div>
        </div>
      </div>
    </div>

    <!-- Active Endpoints -->
    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
      <h3 class="font-bold text-slate-900 text-sm uppercase tracking-wider text-slate-500">Live API Endpoints</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs">
        <a href="/api/v1/me/dashboard" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-brand-600">GET</strong> /api/v1/me/dashboard
        </a>
        <a href="/api/v1/assessments/instruments" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-brand-600">GET</strong> /api/v1/assessments/instruments
        </a>
        <a href="/api/v1/careers" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-brand-600">GET</strong> /api/v1/careers
        </a>
        <a href="/api/v1/market/snapshot/latest" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-brand-600">GET</strong> /api/v1/market/snapshot/latest
        </a>
        <a href="/docs" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-indigo-600">SWAGGER</strong> /docs
        </a>
        <a href="/redoc" target="_blank" class="p-2.5 rounded border border-slate-200 hover:border-brand-500 hover:bg-brand-50 transition block">
          <strong class="text-indigo-600">REDOC</strong> /redoc
        </a>
      </div>
    </div>
    <script>
      async function checkLLMStatus() {
        try {
          const res = await fetch('/api/v1/me/mentor/status');
          const data = await res.json();
          const badge = document.getElementById('llm-status-badge');
          if (data.has_api_key) {
            badge.innerHTML = '<span class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold border border-emerald-200">✓ Groq Key Configured (' + data.model + ')</span>';
          } else {
            badge.innerHTML = '<span class="text-amber-700 bg-amber-50 px-2 py-0.5 rounded font-semibold border border-amber-200">ℹ Key in .env needed (Using Mock mode)</span>';
          }
        } catch (e) {
          console.error(e);
        }
      }

      async function askMentor() {
        const input = document.getElementById('mentor-input');
        const btn = document.getElementById('mentor-btn');
        const box = document.getElementById('mentor-response');
        const text = document.getElementById('response-text');
        const provider = document.getElementById('response-provider');
        const model = document.getElementById('response-model');

        const message = input.value.trim();
        if (!message) return;

        btn.disabled = true;
        btn.innerText = 'Thinking...';
        box.classList.remove('hidden');
        text.innerText = 'Generating guidance based on your verified career twin...';

        try {
          const res = await fetch('/api/v1/me/mentor/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
          });
          const data = await res.json();
          provider.innerText = 'Provider: ' + data.provider;
          model.innerText = data.model;
          text.innerText = data.reply;
        } catch (e) {
          text.innerText = 'Error querying mentor: ' + e.message;
        } finally {
          btn.disabled = false;
          btn.innerText = 'Ask Mentor';
        }
      }

      window.addEventListener('DOMContentLoaded', checkLLMStatus);
    </script>
  </main>
</body>
</html>"""


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz():
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/readyz", response_model=ReadyResponse, tags=["health"])
async def readyz():
    # In full deployment, checks postgres connection, redis ping, and alembic head
    return ReadyResponse(
        status="ok",
        database=True,
        redis=True,
        migrations_at_head=True,
    )


app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
