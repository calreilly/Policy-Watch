from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Counters
REQUEST_COUNTER = Counter(
    "policywatch_requests_total",
    "Total number of API requests",
    ["method", "endpoint"]
)

NODE_EXECUTION_COUNTER = Counter(
    "policywatch_node_executions_total",
    "Number of times each LangGraph node is executed",
    ["node"]
)

TOKEN_USAGE_COUNTER = Counter(
    "policywatch_tokens_used_total",
    "Total number of LLM tokens used",
    ["model"]
)

# Histograms
NODE_PROCESSING_TIME = Histogram(
    "policywatch_node_processing_seconds",
    "Time spent processing each LangGraph node",
    ["node"]
)

# Gauges
VECTOR_STORE_SIZE = Gauge(
    "policywatch_vector_store_size",
    "Number of vectors stored in ChromaDB"
)

def record_request(method: str, endpoint: str):
    REQUEST_COUNTER.labels(method=method, endpoint=endpoint).inc()

def record_node_execution(node: str):
    NODE_EXECUTION_COUNTER.labels(node=node).inc()

def record_node_time(node: str, duration_seconds: float):
    NODE_PROCESSING_TIME.labels(node=node).observe(duration_seconds)

def record_token_usage(model: str, count: int):
    TOKEN_USAGE_COUNTER.labels(model=model).inc(count)

def set_vector_store_size(size: int):
    VECTOR_STORE_SIZE.set(size)

def get_metrics_response():
    return generate_latest()
