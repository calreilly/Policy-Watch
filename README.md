# PolicyWatch: Agentic Legislative AI Platform

PolicyWatch is an advanced, production-ready legislative analysis platform designed to transform raw Congressional data into actionable intelligence. Built with a multi-agent LangGraph orchestrator, it leverages GraphRAG (Neo4j), hybrid vector search (ChromaDB + BM25), and real-time web scraping to provide unprecedented depth into current policy movements.

## 🚀 Key Features

- **Agentic Brief Generator**: A multi-agent pipeline that autonomously researches, synthesizes, and drafts complex policy briefs. Features real-time **SSE (Server-Sent Events) streaming** for transparent execution traces.
- **RAG Policy Assistant**: A persistent, floating AI chatbot for rapid-fire Q&A against the internal legislative database.
- **GraphRAG Visualizer**: An interactive 2D context graph mapping relationships between bills and policy domains using Neo4j-style node-link architecture.
- **Live Legislative Pulse**: Real-time ticker and dashboard feed pulling live data from Congress.gov (v3 API) and the broader web.
- **Persistent Error Logging**: Centralized error tracking that logs system exceptions to disk for high-reliability auditing.

## 🛠️ Technology Stack

- **Backend**: FastAPI, LangGraph (Multi-Agent Orchestration), SQLAlchemy.
- **Intelligence**: OpenAI GPT-4o-mini, ChromaDB (Vector Search), BM25 (Keyword Heuristics), NetworkX (Knowledge Graph).
- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion, Lucide React.
- **Deployment**: Docker, Docker Compose.

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### Local Development Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/calreilly/Policy-Watch.git
   cd Policy-Watch
   ```

2. **Configure Environment**:
   Create a `.env` file in the `backend/` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Orchestrate with Docker**:
   ```bash
   docker-compose up --build
   ```
   - Frontend will be available at: `http://localhost:5175`
   - Backend API will be available at: `http://localhost:8001`

## 📊 Architecture

The system utilizes a hierarchical multi-agent structure:
1. **Supervisor**: Decomposes user queries and delegates to specialized workers.
2. **Congress MCP**: Extracts structured schemas directly from Congress.gov.
3. **RAG Analyst**: Performs semantic lookups via ChromaDB.
4. **Web Scraper**: Scrapes live news and web data via DuckDuckGo.
5. **Graph Analyst**: Maps relationship dependencies via NetworkX.
6. **Manager**: Synthesizes all worker outputs into a final Chain-of-Thought brief.

## 📝 Usage

- **Synthesize a Brief**: Navigate to the "Brief Generator," enter a legislative topic (e.g., "AI Regulation in healthcare"), and watch the agents work in real-time.
- **Chat with Congress**: Use the floating bubble in the bottom right to ask quick questions about specific bills.
- **Audit Logs**: Access system logs at `http://localhost:8001/api/agent/error-log` for post-testing analysis.

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Created as a GRAD 5900 Capstone Project.*
