import { useState } from 'react';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import { motion } from 'framer-motion';
import { Bot, Sparkles, Network, Globe } from 'lucide-react';
import PipelineViz from '../components/PipelineViz';
import TrustScore from '../components/TrustScore';
import API_BASE_URL from '../api_config';

const mdParser = new MarkdownIt();

export default function BriefGenerator() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [brief, setBrief] = useState(null);
  const [trace, setTrace] = useState([]);
  const [score, setScore] = useState(0);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setTrace([]);
    setBrief("");
    setScore(0);
    setError(null);
    
    // Set up Server-Sent Events (SSE) with error handling
    const eventSource = new EventSource(`${API_BASE_URL}/api/agent/stream-brief?query=${encodeURIComponent(query)}`);

    // Reasoning steps
    eventSource.addEventListener('reasoning', (e) => {
        const stepData = JSON.parse(e.data);
        setTrace(prev => [...prev, stepData]);
    });

    // Completion event
    eventSource.addEventListener('complete', (e) => {
        const result = JSON.parse(e.data);
        setBrief(result.brief);
        setScore(result.trust_score);
        setLoading(false);
        eventSource.close();
    });

    // Custom error events from backend
    eventSource.addEventListener('error_event', (e) => {
        try {
            const err = JSON.parse(e.data);
            setError(`Agent error: ${err.message}`);
        } catch {
            setError('An unknown error occurred during processing.');
        }
        setLoading(false);
        eventSource.close();
    });

    // Generic network errors / connection loss
    eventSource.onerror = (err) => {
        console.error('SSE streaming error', err);
        if (!error) {
            setError('Connection lost. Please try again.');
        }
        setLoading(false);
        eventSource.close();
    };
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="glass-panel p-8 md:p-12 relative overflow-hidden text-center bg-gradient-to-b from-primary/5 to-transparent border-t-primary/30">
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/20 blur-3xl rounded-full"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-secondary/20 blur-3xl rounded-full"></div>
        
        <div className="relative z-10 max-w-3xl mx-auto">
          <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-2xl mb-6 shadow-inner ring-1 ring-primary/20">
            <Bot size={32} className="text-primary" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">Agentic Policy Generator</h1>
          <p className="text-textMuted text-lg mb-10 leading-relaxed">
            Construct exhaustive analytical briefs autonomously. Our multi-agent LLM harnesses <strong className="text-white font-semibold">GraphRAG Neo4j</strong> networks, BM25 Hybrid indexing, and live <strong className="text-white font-semibold">Web Search Scrapers</strong>.
          </p>
          
          <div className="space-y-4">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Provide an intelligence brief on emerging Congressional data privacy legislation..."
              rows="3"
              className="input-styled text-lg shadow-inner resize-none focus:ring-2"
            />
            <button 
              onClick={handleGenerate}
              disabled={loading || !query.trim()}
              className="btn-primary w-full md:w-auto text-lg px-12 py-4 flex items-center justify-center gap-2 mx-auto disabled:opacity-60"
            >
              {loading ? (
                <><span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Processing Network...</>
              ) : (
                <><Sparkles size={20} /> Synthesize Brief</>
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="glass-panel p-6 bg-red-500/10 border-red-500/20 text-red-200 text-center animate-in fade-in slide-in-from-top-2">
          {error}
        </div>
      )}

      {brief && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 lg:grid-cols-12 gap-8"
        >
          {/* Brief Panel */}
          <div className="lg:col-span-8 glass-panel p-8 xl:p-10">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 pb-6 border-b border-border/60">
              <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">Executive Report</h2>
              <TrustScore score={score} />
            </div>
            <div 
              className="markdown-body text-lg text-textMain" 
              dangerouslySetInnerHTML={{ __html: mdParser.render(brief) }} 
            />
          </div>

          {/* Trace Panel */}
          <div className="lg:col-span-4 glass-panel p-6">
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-border/60">
              <Network size={20} className="text-secondary" />
              <h3 className="font-bold text-lg text-white">LangGraph Execution Trace</h3>
            </div>
            <PipelineViz trace={trace} />
          </div>
        </motion.div>
      )}
    </div>
  );
}
