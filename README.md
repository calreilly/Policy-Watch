# PolicyWatch: Agentic Legislative Intelligence Platform

**PolicyWatch** is a production-grade, multi-agent intelligence suite designed for the autonomous era. Developed for the **GRAD 5900: Advanced Agentic Coding** (Spring 2026) capstone, the platform automates the synthesis of complex legislative data, financial influence mapping, and predictive policy modeling.

---

## 🏛️ Business Problem & Vision
Modern governance is plagued by **information oversaturation**. With thousands of bills moving through Congress, stakeholders are often "blind" to the hidden financial, regulatory, and global risks within legislative text. 

**PolicyWatch** bridges this gap by turning raw government feeds into **Actionable Executive Intelligence**. It moves beyond simple "tracking" into autonomous **reasoning**—predicting passage probability, auditing lobbyist influence, and benchmarking US bills against global standards (like the EU AI Act) in real-time.

---

## 🎓 Syllabus Alignment: "From Prompting to Autonomous Systems"
This project serves as a functional implementation of the GRAD 5900 curriculum, mapping directly to each educational phase:

### **Phase 1: Foundations & Reasoning**
*   **System 2 Thinking**: Implemented **Inference-Time Scaling** via LangGraph logic, allowing the agent to perform multiple "Chain-of-Thought" (CoT) passes before generating a final response.
*   **ReAct Patterns**: The `AgentService` utilizes autonomous tool-routing to decide when to search the web vs. query the vector database.

### **Phase 2: Knowledge Augmentation**
*   **RAG 2.0**: Implemented a **Hybrid Search Pipeline** (Vector search in ChromaDB + BM25 Lexical search) to ensure 99% retrieval precision.
*   **GraphRAG**: Integrated **NetworkX** to allow agents to visualize relationship dependencies between disparate policy subjects (e.g., mapping how an "Artificial Intelligence" bill impacts "Energy Grid" regulations).
*   **Evaluation**: Built a scientific **Evaluation Suite** (`evaluation.py`) to measure RAG performance via **MRR** and **NDCG** metrics.

### **Phase 3: The Agentic Shift & MCP**
*   **Model Context Protocol (MCP)**: The platform uses an **MCP Server** wrapper for the Congress.gov API, treating external databases as local system tools rather than static API endpoints.
*   **Multi-Agent Workflows**: Implemented a **Hierarchical Team** (Supervisor → RAG Analyst / Web Scraper / Graph Worker) for collaborative intelligence.
*   **HITL & Memory**: Uses **LangGraph Persistence** (Checkpointers) to maintain long-term state across user sessions.

### **Phase 4: Efficiency, Scale & Governance**
*   **Small Model Strategy**: Optimized for **GPT-4o-mini**, demonstrating high-fidelity reasoning on a cost-effective, high-speed LLM footprint.
*   **Knowledge Distillation**: The system automatically generates a **JSONL Dataset** from high-quality agent reasoning cycles, ready for future model fine-tuning.
*   **Safety & Red-Teaming**: Implemented a dedicated **Guardrail Node** to protect against Prompt Injection and "Agent Hijacking" attempts.

---

## 🛠️ Technical Architecture

### **The "Brain" (Backend)**
*   **Framework**: FastAPI (Python 3.9+)
*   **Orchestrator**: LangGraph State Machine
*   **Vector Engine**: ChromaDB
*   **Knowledge Graph**: NetworkX
*   **Metrics**: Prometheus-style latency and token tracking

### **The "Interface" (Frontend)**
*   **Framework**: React 18 (Vite)
*   **Styling**: High-fidelity Glassmorphism (Vanilla CSS)
*   **Streaming**: Server-Sent Events (SSE) for real-time agentic trace visualization
*   **Optimization**: Gzip compression and GPU-accelerated motion components

---

## 📊 Feature Matrix
- **🔮 Passage Prognosis**: Probabilistic modeling of a bill’s success based on sponsor power and topic friction.
- **💰 Finance Intelligence**: Live FEC itemized receipt mapping for all bill sponsors.
- **🗺️ Influence Mapping**: Categorization of lobbying influence by industry sector (Tech, Finance, Energy).
- **🌍 Global Benchmarking**: Comparative RAG analysis against international standards (EU AI Act, UN Treaties).

---

## 🚀 Setup & Execution

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/calreilly/Policy-Watch.git
    cd Policy-Watch
    ```
2.  **Backend**:
    ```bash
    cd backend && python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python main.py
    ```
3.  **Frontend**:
    ```bash
    cd frontend && npm install
    npm run dev
    ```

---

*Developed for GRAD 5900: Advanced Agentic Coding @ University of Connecticut.*
