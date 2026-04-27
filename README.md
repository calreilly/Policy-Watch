# PolicyWatch: Legislative Intelligence Platform

**PolicyWatch** is a next-generation, multi-agent legislative tracking and intelligence platform designed for the agentic era. Beyond simple bill tracking, PolicyWatch synthesizes data from multiple federal and state sources, analyzes public sentiment, benchmarks against international standards, and provides deep-box AI impact reports.

---

## 🏛️ System Core Features

### 1. Multi-Agent Data Orchestration
The platform utilizes a coordinated agentic network to fetch, clean, and synchronize data from:
*   **Congress.gov (Official)**: Primary source for US Federal legislation.
*   **GovTrack**: Legislative prognosis and advanced member telemetry.
*   **Federal Register**: Executive orders and agency-level regulatory actions.
*   **OpenStates**: State-level legislative tracking.

### 2. Transparency Engine (FEC Integration)
PolicyWatch maps financial influence directly to legislative action by integrating live **OpenFEC** data.
*   **Sponsor Financing**: View total funds raised, spent, and cash-on-hand for lead sponsors.
*   **Transparency Score**: High-visibility financial cards in Every bill modal.

### 3. Automated Regulatory Impact Statement (ARIS)
An on-demand AI analyst that performs deep-dive fiscal and regulatory risk assessments.
*   **Mandate Discovery**: Identifies hidden regulatory requirements for the private sector.
*   **Fiscal Tracking**: Extracts spending authorizations and potential budgetary impacts.
*   **Beneficiary Analysis**: Pinpoints primary stakeholders and gainers.

### 4. Public Sentiment Pulse
Real-time monitoring of the public discourse surrounding specific legislation.
*   **Social Vector Scanning**: Scrapes Reddit, X, and professional policy blogs.
*   **Sentiment Gauge**: Visualizes public support/opposition with an AI-synthesized "Public Voice" summary.

### 5. Global Policy Benchmarking (International RAG)
Comparative analysis between US bills and international regulatory standards.
*   **Cross-Jurisdictional Logic**: Benchmarks AI and Tech legislation against the **EU AI Act**, UN treaties, and OECD guidelines.
*   **Alignment Score**: Quantitative measure of how closely a US bill aligns with global policy standards.

---

## 🚀 Tech Stack

### Backend
*   **Framework**: FastAPI (Python 3.9+)
*   **Vector Database**: ChromaDB (Hybrid RAG: BM25 + Vector Search)
*   **LLM Orchestration**: OpenAI (`gpt-4o-mini`)
*   **Database**: SQLAlchemy (SQLite for high-performance edge caching)

### Frontend
*   **Framework**: React (Vite)
*   **Styling**: Vanilla CSS with modern Glassmorphism aesthetics.
*   **Animations**: Framer Motion
*   **Icons**: Lucide-React

---

## 🛠️ Installation & Setup

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)
*   OpenAI API Key

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys here
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Evaluation Framework
PolicyWatch uses a formal evaluation suite to ensure RAG accuracy, tracking metrics such as:
*   **MRR (Mean Reciprocal Rank)**
*   **NDCG (Normalized Discounted Cumulative Gain)**
*   **Pipeline Trace**: Step-by-step latency and action tracking for every agentic cycle.

---

## 🗺️ Roadmap
*   [x] Multi-Source Integration (Phase 1)
*   [x] FEC Transparency Engine (Phase 2)
*   [x] ARIS Impact Analysis (Phase 2)
*   [x] Social Sentiment Pulse (Phase 2)
*   [x] Global Policy RAG (Phase 2)
*   [ ] Predictive Passage Modeling (Phase 3)
*   [ ] Lobbyist Financial Mapping (Phase 3)

---

Developed for **GRAD5900: Advanced Agentic Coding**.
