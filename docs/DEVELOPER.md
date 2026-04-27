# PolicyWatch Developer Guide

## Architecture Overview
PolicyWatch is an AI-powered RAG platform for legislative analysis.

- **Backend**: FastAPI with LangGraph for agentic orchestration.
- **Frontend**: React 18 with Vite and Tailwind CSS.
- **RAG**: ChromaDB for vector storage, OpenAI for embeddings and inference.
- **Data**: Live feeds from Congress.gov API.

## setup
1. `cd backend && pip install -r requirements.txt`
2. Create `.env` with `OPENAI_API_KEY`.
3. `uvicorn main:app --reload --port 8001`
4. `cd frontend && npm install && npm run dev`

## Agent Workflow
The agent uses a StateGraph with the following nodes:
- `guardrail`: Safety check.
- `supervisor`: Multi-agent decomposition.
- `congress_mcp`: Tool-based data retrieval.
- `rag_analyst`: Vector similarity search.
- `web_scraper`: Real-time news.
- `graph_analyst`: Knowledge graph analysis.
- `manager_reasoning`: COT synthesis.
- `generate_brief`: MD Output generation.

## Monitoring
- `/metrics`: Prometheus metrics.
- `/api/health`: Comprehensive health status.
- `/api/admin/cost-analytics`: Token usage and costs.
