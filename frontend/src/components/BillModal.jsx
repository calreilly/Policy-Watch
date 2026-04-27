import { useEffect, useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Activity, ExternalLink, Network, CheckCircle, XCircle, Sparkles, Globe, Zap } from 'lucide-react';
import API_BASE_URL from '../api_config';

export default function BillModal({ billId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [govtrack, setGovtrack] = useState(null);
  const [fedReg, setFedReg] = useState([]);
  const [report, setReport] = useState("");
  const [pulse, setPulse] = useState(null);
  const [alignment, setAlignment] = useState(null);
  const [influence, setInfluence] = useState(null);
  const [prognosis, setPrognosis] = useState(null);
  const [activeTab, setActiveTab] = useState("overview"); 
  const [generatingReport, setGeneratingReport] = useState(false);
  const [loadingPulse, setLoadingPulse] = useState(false);
  const [loadingAlignment, setLoadingAlignment] = useState(false);
  const [loadingInfluence, setLoadingInfluence] = useState(false);
  const [loadingPrognosis, setLoadingPrognosis] = useState(false);
  const [loading, setLoading] = useState(true);

  const generateAIReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/analysis/impact-report/${billId}`);
      setReport(res.data.report);
    } catch (err) {
      console.error("Report generation failed", err);
    } finally {
      setGeneratingReport(false);
    }
  };

  useEffect(() => {
    if (!billId) return;
    setLoading(true);
    
    // Split billId (119-HR-8191) to parts for separate API searches
    const [congress, type, number] = billId.split('-');

    const fetchAll = async () => {
      try {
        const [billRes, gtRes, frRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/bills/${billId}`),
          axios.get(`${API_BASE_URL}/api/govtrack/bills?query=${number}&congress=${congress}`).catch(() => null),
          axios.get(`${API_BASE_URL}/api/federal-register/search?query=${number}+${type}&limit=2`).catch(() => null)
        ]);

        setDetail(billRes.data);
        
        // Find exact match in GovTrack results
        if (gtRes?.data?.results) {
           const match = gtRes.data.results.find(b => b.number == number && b.bill_type_label?.toUpperCase() === type.toUpperCase());
           setGovtrack(match);
        }
        
        if (frRes?.data?.results) setFedReg(frRes.data.results);

        // Fetch Social Sentiment Pulse
        setLoadingPulse(true);
        axios.post(`${API_BASE_URL}/api/analysis/sentiment/${billId}`)
          .then(res => setPulse(res.data.pulse))
          .catch(e => console.error("Pulse fetch failed", e))
          .finally(() => setLoadingPulse(false));
          
        // Fetch Global Alignment
        setLoadingAlignment(true);
        axios.post(`${API_BASE_URL}/api/analysis/global-alignment/${billId}`)
          .then(res => setAlignment(res.data.alignment))
          .catch(e => console.error("Alignment fetch failed", e))
          .finally(() => setLoadingAlignment(false));

        // Fetch Lobbying Influence
        setLoadingInfluence(true);
        axios.post(`${API_BASE_URL}/api/analysis/lobbying/${billId}`)
          .then(res => setInfluence(res.data.influence))
          .catch(e => console.error("Lobbying fetch failed", e))
          .finally(() => setLoadingInfluence(false));

        // Fetch Passage Prognosis (Phase 3)
        setLoadingPrognosis(true);
        axios.post(`${API_BASE_URL}/api/analysis/prognosis/${billId}`)
          .then(res => setPrognosis(res.data.prognosis))
          .catch(e => console.error("Prognosis fetch failed", e))
          .finally(() => setLoadingPrognosis(false));

      } catch (err) {
        console.error("Modal multi-fetch error", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [billId]);

  return (
    <AnimatePresence>
      {billId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />
          
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="relative w-full max-w-4xl max-h-[85vh] bg-[#12121c] border border-primary/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          >
            {loading || !detail ? (
              <div className="p-12 flex flex-col items-center justify-center h-64">
                <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-textMuted uppercase tracking-widest text-sm font-bold">Extracting Multi-Agent Intelligence...</p>
              </div>
            ) : (
              <>
                <div className="p-6 border-b border-white/5 bg-[#181824] flex justify-between items-start sticky top-0 z-10">
                  <div>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-primary/20 text-primary text-xs font-semibold mb-3 tracking-widest">
                      <Activity size={12} /> {detail.id}
                    </span>
                    <h2 className="text-2xl font-bold text-white mb-2 leading-tight pr-8">{detail.title}</h2>
                    <p className="text-textMuted text-sm line-clamp-2">{detail.summary}</p>
                  </div>
                  <button onClick={onClose} className="p-2 bg-black/20 hover:bg-white/10 rounded-full transition-colors absolute top-6 right-6">
                    <X size={20} className="text-white" />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <div className="p-8 space-y-10 focus:outline-none">
                      
                      {/* Intelligence Matrix Navigation */}
                      <div className="flex items-center justify-between border-b border-white/5 pb-6">
                        <div className="flex gap-2 bg-black/60 p-1 rounded-full border border-white/10 backdrop-blur-md">
                          {["overview", "intelligence", "analysis"].map(tab => (
                            <button
                              key={tab}
                              onClick={() => setActiveTab(tab)}
                              className={`px-6 py-2 rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${
                                activeTab === tab ? 'bg-primary text-black shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)]' : 'text-textMuted hover:text-white'
                              }`}
                            >
                              {tab}
                            </button>
                          ))}
                        </div>
                        <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full border border-success/20 bg-success/5">
                           <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
                           <span className="text-[9px] font-black text-success uppercase tracking-widest">Autonomous Sync Active</span>
                        </div>
                      </div>

                      {activeTab === "overview" && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                          <div className="lg:col-span-2 space-y-10">
                            <div className="group">
                              <h3 className="text-[10px] uppercase tracking-[0.2em] text-primary font-black mb-4 flex items-center gap-2">
                                <Activity size={14} /> Legislative Synthesis
                              </h3>
                              <p className="text-white text-xl leading-relaxed font-semibold tracking-tight">
                                {detail.summary || "Agentic synthesis in progress..."}
                              </p>
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                              <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/5 group hover:border-primary/30 transition-all duration-500">
                                <span className="text-[9px] uppercase tracking-widest text-textMuted block mb-2 font-black">Current Status</span>
                                <span className="text-white font-black text-lg">{detail.status}</span>
                              </div>
                              <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-white/5 group hover:border-primary/30 transition-all duration-500 text-right">
                                <span className="text-[9px] uppercase tracking-widest text-textMuted block mb-2 font-black">Submission Date</span>
                                <span className="text-white font-black text-lg">{detail.introduced_date}</span>
                              </div>
                            </div>

                            <div className="glass-panel p-6 rounded-[2rem] border border-white/5 bg-white/5">
                              <h3 className="text-[10px] uppercase tracking-[0.2em] text-textMuted font-black mb-6 flex items-center gap-2">
                                <Users size={14} /> Lead Proponents
                              </h3>
                              <div className="flex flex-wrap gap-3">
                                {(detail.sponsors || []).map((s, idx) => (
                                  <div key={idx} className={`px-5 py-3 rounded-xl border border-white/5 bg-black/40 text-xs font-black shadow-xl ${s.party === 'D' ? 'text-blue-400' : 'text-red-400'}`}>
                                    {s.member_name} <span className="opacity-50 ml-1">[{s.party}-{s.state}]</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>

                          <div className="space-y-8">
                            <div className="glass-panel p-6 rounded-3xl border border-white/5 bg-white/5">
                                <h3 className="text-[10px] uppercase tracking-[0.2em] text-textMuted font-black mb-6 flex items-center gap-2">
                                  <Network size={14} /> Matrix Connections
                                </h3>
                                <div className="space-y-3">
                                  {(detail.related_bills || []).map((rb, idx) => (
                                    <div key={idx} className="text-[11px] font-mono bg-secondary/5 border border-secondary/20 text-secondary px-3 py-2 rounded-lg block hover:bg-secondary/10 transition-colors">
                                      {rb}
                                    </div>
                                  ))}
                                </div>
                            </div>

                            <div className="glass-panel p-6 rounded-3xl border border-primary/20 bg-primary/5 relative overflow-hidden group">
                               <div className="absolute top-3 right-3 px-2 py-0.5 bg-primary text-[8px] font-black text-black rounded-sm uppercase tracking-widest">Phase 3</div>
                               <h3 className="text-[10px] uppercase tracking-[0.2em] text-primary font-black mb-4">Passage Prognosis</h3>
                               {loadingPrognosis ? (
                                  <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                     <div className="h-full bg-primary/40 w-full animate-progress"></div>
                                  </div>
                               ) : prognosis ? (
                                  <div className="space-y-3">
                                     <div className="flex justify-between items-end">
                                        <span className="text-3xl font-black text-white tracking-tighter">{Math.round(prognosis.score * 100)}%</span>
                                        <span className={`text-[10px] font-black uppercase tracking-widest ${prognosis.momentum === 'high' ? 'text-success' : 'text-textMuted'}`}>
                                          {prognosis.momentum} Momentum
                                        </span>
                                     </div>
                                     <p className="text-[10px] text-white/70 leading-relaxed font-medium">"{prognosis.reasoning}"</p>
                                  </div>
                               ) : (
                                  <p className="text-[10px] text-textMuted italic">Telemetry Offline</p>
                               )}
                            </div>
                          </div>
                        </div>
                      )}

                      {activeTab === "intelligence" && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in zoom-in-95 duration-500">
                          {/* Financial Panel */}
                          <div className="glass-panel p-8 rounded-[2.5rem] border border-red-500/10 bg-red-500/5 hover:bg-red-500/10 transition-all flex flex-col justify-between h-full group">
                            <div>
                               <h3 className="text-[10px] uppercase tracking-[0.2em] text-red-400 font-black mb-8 flex items-center gap-2">
                                  <Zap size={14} className="group-hover:animate-bounce" /> Finance: OpenFEC
                               </h3>
                               {detail.finance ? (
                                  <div className="space-y-8">
                                     <div>
                                        <p className="text-[10px] uppercase text-textMuted mb-2 font-black">Capital Inflow</p>
                                        <p className="text-4xl font-black text-white tracking-tighter">${detail.finance.total_raised.toLocaleString()}</p>
                                     </div>
                                     <div className="flex justify-between items-end border-t border-white/10 pt-6">
                                        <div>
                                           <p className="text-[9px] uppercase text-textMuted mb-1 font-black">Disbursements</p>
                                           <p className="text-lg font-black text-white">${Math.round(detail.finance.total_spent/1000)}k</p>
                                        </div>
                                        <div className="text-right text-success font-black text-[10px] tracking-widest bg-success/10 px-2 py-1 rounded">
                                           HEALTHY
                                        </div>
                                     </div>
                                  </div>
                               ) : <p className="text-xs text-textMuted italic">Telemetry Offline</p>}
                            </div>
                          </div>

                          {/* Influence Panel */}
                          <div className="glass-panel p-8 rounded-[2.5rem] border border-warning/10 bg-warning/5 hover:bg-warning/10 transition-all flex flex-col h-full group">
                             <h3 className="text-[10px] uppercase tracking-[0.2em] text-warning font-black mb-8 flex items-center gap-2">
                                <Users size={14} /> Influence Map
                             </h3>
                             {influence ? (
                                <div className="space-y-5 flex-1">
                                   {influence.sectors.slice(0, 4).map((s, idx) => (
                                      <div key={idx} className="group/item">
                                         <div className="flex justify-between text-[11px] mb-2">
                                            <span className="text-white font-black uppercase tracking-tight">{s.name}</span>
                                            <span className="text-textMuted font-mono">${Math.round(s.amount/1000)}k</span>
                                         </div>
                                         <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                            <motion.div 
                                              initial={{ width: 0 }}
                                              animate={{ width: `${(s.amount / influence.sectors[0].amount) * 100}%` }}
                                              className="h-full bg-warning/40 group-hover/item:bg-warning transition-colors" />
                                         </div>
                                      </div>
                                   ))}
                                </div>
                             ) : <div className="animate-pulse h-48 bg-white/5 rounded-2xl"></div>}
                          </div>

                          {/* Pulse & Global Metrics */}
                          <div className="space-y-6 flex flex-col">
                             <div className="glass-panel p-8 rounded-[2.5rem] border border-secondary/10 bg-secondary/5 h-1/2 flex flex-col justify-between group">
                                <h3 className="text-[10px] uppercase tracking-[0.2em] text-secondary font-black mb-4 flex items-center gap-2">
                                   <Activity size={14} /> Public Pulse
                                </h3>
                                {pulse ? (
                                   <div className="flex items-center gap-5">
                                      <div className="w-20 h-20 rounded-full border-[8px] border-secondary/10 flex items-center justify-center relative shadow-2xl shadow-secondary/20">
                                         <span className="text-sm font-black text-white">{Math.round(pulse.score * 100)}%</span>
                                         <svg className="absolute -rotate-90 w-full h-full p-[-8px]">
                                            <circle cx="40" cy="40" r="32" fill="transparent" stroke="currentColor" strokeWidth="8" className="text-secondary shadow-lg" strokeDasharray={`${pulse.score * 201} 201`} />
                                         </svg>
                                      </div>
                                      <div className="flex-1">
                                         <p className="text-xs font-black text-white uppercase mb-1 tracking-tighter">{pulse.label}</p>
                                         <p className="text-[10px] text-textMuted italic leading-tight">"{pulse.summary}"</p>
                                      </div>
                                   </div>
                                ) : <div className="h-full bg-white/5 rounded-2xl animate-pulse"></div>}
                             </div>

                             <div className="glass-panel p-8 rounded-[2.5rem] border border-[#4ade80]/10 bg-[#4ade80]/5 h-1/2 flex flex-col justify-between group">
                                <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#4ade80] font-black mb-4 flex items-center gap-2">
                                   <Globe size={14} /> Global RAG
                                </h3>
                                {alignment ? (
                                   <div className="space-y-4">
                                      <p className="text-xs text-white font-black leading-tight group-hover:text-[#4ade80] transition-colors">{alignment.standard}</p>
                                      <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-[#4ade80]">
                                         <span className="opacity-60">Match Score:</span>
                                         <span>{Math.round(alignment.alignment_score * 100)}%</span>
                                      </div>
                                      <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                         <div className="h-full bg-[#4ade80]/50" style={{width: `${alignment.alignment_score * 100}%`}}></div>
                                      </div>
                                   </div>
                                ) : <div className="h-full bg-white/5 rounded-2xl animate-pulse"></div>}
                             </div>
                          </div>
                        </div>
                      )}

                      {activeTab === "analysis" && (
                        <div className="space-y-10 animate-in slide-in-from-right-8 duration-500 max-w-4xl mx-auto">
                           <button 
                             onClick={generateAIReport}
                             disabled={generatingReport}
                             className="w-full group relative flex items-center justify-center gap-5 py-10 rounded-[3rem] bg-gradient-to-br from-primary/20 to-transparent border-2 border-primary/20 overflow-hidden shadow-2xl shadow-primary/10"
                           >
                             <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                             <Sparkles size={32} className={generatingReport ? 'animate-spin text-white' : 'text-primary scale-110 group-hover:rotate-12 transition-all'} />
                             <div className="text-left">
                               <p className="text-xs uppercase font-black text-primary/60 tracking-[0.3em] mb-1">Agentic Risk Scoring</p>
                               <span className="text-2xl font-black text-white">{generatingReport ? 'Synthesizing Decision Matrix...' : 'Generate Full Impact Statement'}</span>
                             </div>
                           </button>

                           {report && (
                             <div className="glass-panel p-10 rounded-[3rem] border border-primary/20 bg-[#0d0d14] relative shadow-2xl">
                               <div className="absolute -top-3 left-10 px-6 py-1.5 bg-primary text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full shadow-lg">ARIS OUTPUT :: SECURED</div>
                               <div className="text-white/90 leading-loose text-base font-medium space-y-4" dangerouslySetInnerHTML={{ __html: report.replace(/\n/g, '<br/>') }} />
                             </div>
                           )}
                        </div>
                      )}
                    </div>
                </div>
                
                <div className="p-4 border-t border-white/5 bg-[#181824] flex justify-end">
                   <button onClick={() => window.open(detail.url, '_blank')} className="flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-secondary text-white text-sm font-bold rounded-lg transition-colors">
                     <ExternalLink size={16} /> Open Origin Document
                   </button>
                </div>
              </>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
