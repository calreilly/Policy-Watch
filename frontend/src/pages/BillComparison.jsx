import { useState, useEffect } from 'react';
import axios from 'axios';
import { Network, Search, AlertTriangle, FileText, ChevronRight, Zap } from 'lucide-react';
import API_BASE_URL from '../api_config';

export default function BillComparison() {
  const [bills, setBills] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/bills/today`)
      .then(res => setBills(res.data.bills || []))
      .catch(err => console.error("Fetch error", err));
  }, []);

  const toggleBill = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else if (selectedIds.length < 2) {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const generateComparison = async () => {
    if (selectedIds.length !== 2) return;
    setLoading(true);
    setReport(null);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/comparison/compare-bills`, {
        bill_ids: selectedIds
      });
      setReport(res.data);
    } catch (err) {
      setError("Failed to generate comparative analysis. The agents might be under high负载.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 border-b border-white/5 pb-8">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Network size={16} className="text-secondary animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-secondary">Cross-Legislative Intelligence</span>
          </div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight leading-tight">Comparative Analysis</h1>
          <p className="text-textMuted text-lg max-w-2xl mt-2">Compare structural impacts and regulatory overlaps across multiple bills using the GraphRAG reasoning engine.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Selection Sidebar */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-panel p-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
              <Search size={14} className="text-primary" /> Selection Console (Pick 2)
            </h3>
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
              {bills.map(bill => (
                <button
                  key={bill.id}
                  onClick={() => toggleBill(bill.id)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-300 ${
                    selectedIds.includes(bill.id)
                      ? 'bg-primary/20 border-primary shadow-lg shadow-primary/10'
                      : 'bg-white/5 border-white/5 hover:border-white/20'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[10px] font-bold text-primary uppercase bg-primary/10 px-1.5 py-0.5 rounded leading-none">{bill.id}</span>
                    {selectedIds.includes(bill.id) && <Zap size={12} className="text-primary fill-primary" />}
                  </div>
                  <h4 className="text-sm font-semibold text-white line-clamp-2 leading-snug">{bill.title}</h4>
                </button>
              ))}
            </div>
            <button
              onClick={generateComparison}
              disabled={selectedIds.length !== 2 || loading}
              className="btn-primary w-full mt-6 py-4 flex items-center justify-center gap-2"
            >
              {loading ? <><span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Processing Matrix...</> : <><Network size={18} /> Generate Comparison</>}
            </button>
          </div>
        </div>

        {/* Report Area */}
        <div className="lg:col-span-8">
          {report ? (
            <div className="glass-panel p-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/5">
                <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-textMuted text-white">Analysis Report</h3>
                <div className="px-3 py-1 bg-success/10 border border-success/20 rounded-full">
                  <span className="text-[10px] font-bold text-success uppercase tracking-tighter">Confidence High</span>
                </div>
              </div>
              
              <div className="space-y-8">
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(report.comparisons).map(([id, data]) => (
                    <div key={id} className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <p className="text-[10px] uppercase font-bold text-primary mb-1">{id}</p>
                      <p className="text-xs font-semibold text-white leading-tight">{data.title}</p>
                      <p className="text-[10px] text-textMuted mt-1">Status: {data.status}</p>
                    </div>
                  ))}
                </div>

                <div className="prose prose-invert max-w-none space-y-6">
                  {Object.entries(report.comparisons).map(([id, data]) => (
                    <div key={`body-${id}`} className="p-6 bg-[#0d0d14] rounded-2xl border border-white/5 shadow-inner">
                      <h4 className="text-secondary font-bold text-sm uppercase tracking-widest mb-4">Impact Analysis: {id}</h4>
                      <p className="text-textMain text-sm leading-relaxed mb-4">{data.impact.budgetary_impact}</p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {data.impact.sectors.map(s => <span key={s} className="px-2 py-0.5 bg-primary/10 text-primary text-[10px] rounded uppercase font-bold">{s}</span>)}
                      </div>
                      <p className="text-xs text-textMuted italic">Risks identified: {data.impact.risks}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : loading ? (
             <div className="glass-panel p-12 flex flex-col items-center justify-center h-full border-dashed border-2">
                <div className="w-12 h-12 border-4 border-secondary border-t-transparent rounded-full animate-spin mb-6"></div>
                <p className="text-textMuted uppercase tracking-widest text-sm font-bold">Agents are correlating vector namespaces...</p>
             </div>
          ) : error ? (
            <div className="glass-panel p-8 bg-red-500/5 border-red-500/20 text-center">
              <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
              <p className="text-white font-semibold mb-2">Matrix Synthesis Failure</p>
              <p className="text-textMuted text-sm">{error}</p>
            </div>
          ) : (
            <div className="glass-panel p-12 flex flex-col items-center justify-center h-full border-dashed border-2 border-white/10 opacity-60">
              <FileText className="text-textMuted mb-4" size={48} />
              <p className="text-textMuted text-lg font-medium">Select two bills from the left console to start comparison.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
