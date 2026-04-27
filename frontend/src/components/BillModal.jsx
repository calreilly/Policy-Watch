import { useEffect, useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Activity, ExternalLink, Network, CheckCircle, XCircle, Sparkles } from 'lucide-react';
import API_BASE_URL from '../api_config';

export default function BillModal({ billId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [govtrack, setGovtrack] = useState(null);
  const [fedReg, setFedReg] = useState([]);
  const [report, setReport] = useState("");
  const [generatingReport, setGeneratingReport] = useState(false);
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

                <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    {/* Left Column */}
                    <div className="space-y-6">
                      <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                        <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                          <Activity size={14} /> Legislative Trajectory
                        </h3>
                        <div className="relative pl-4 border-l-2 border-primary/30 space-y-4">
                           <div className="relative">
                             <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-primary ring-4 ring-[#12121c]"></div>
                             <p className="text-sm font-bold text-white">{detail.latest_action || "Introduced"}</p>
                             <p className="text-xs text-textMuted">{detail.introduced_date}</p>
                           </div>
                        </div>
                      </div>

                      <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                        <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                          <Network size={14} /> Agent Similarity Matrix
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {(detail.related_bills || []).map((rb, idx) => (
                             <span key={idx} className="px-3 py-1 bg-secondary/10 border border-secondary/20 text-secondary text-xs rounded-full font-medium">
                               {rb}
                             </span>
                          ))}
                        </div>
                      </div>

                      <div className="glass-panel p-5 rounded-xl border border-primary/20 bg-primary/5">
                        <h3 className="text-xs uppercase tracking-widest text-primary font-bold mb-4 flex items-center gap-2">
                          <Sparkles size={14} /> Automated Impact Analysis (ARIS)
                        </h3>
                        {report ? (
                          <div className="prose prose-invert prose-xs max-h-64 overflow-y-auto custom-scrollbar bg-black/20 p-4 rounded-lg border border-white/5">
                            <div className="text-[11px] text-textMain whitespace-pre-wrap leading-relaxed">
                              {report}
                            </div>
                          </div>
                        ) : (
                          <button 
                            onClick={generateAIReport}
                            disabled={generatingReport}
                            className="w-full py-3 bg-primary/20 border border-primary/30 text-primary text-xs font-bold uppercase rounded-lg hover:bg-primary/30 transition-all flex items-center justify-center gap-2"
                          >
                            {generatingReport ? (
                              <><span className="w-4 h-4 border-2 border-primary border-t-white rounded-full animate-spin"></span> Processing Matrix...</>
                            ) : (
                              <><Sparkles size={14} /> Generate Deep Intelligence Report</>
                            )}
                          </button>
                        )}
                        <p className="text-[9px] text-textMuted mt-3 uppercase tracking-tighter text-center">
                          Powered by PolicyWatch ARIS Agentic Reasoning
                        </p>
                      </div>
                    </div>

                    {/* Right Column */}
                    <div className="space-y-6">
                      <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                        <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                          <Users size={14} /> Intelligence: Sponsors
                        </h3>
                        <div className="space-y-3">
                          {(detail.sponsors || []).map((s, idx) => (
                            <div key={idx} className="flex justify-between items-center bg-[#0d0d14] p-3 rounded-lg border border-white/5">
                              <span className="text-sm text-white font-medium">{s.member_name}</span>
                              <span className={`text-xs px-2 py-0.5 rounded font-bold ${s.party === 'D' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                                {s.party}-{s.state}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {detail.finance && (
                        <div className="glass-panel p-5 rounded-xl border border-white/5 bg-[#1a1a2e]/50">
                          <h3 className="text-xs uppercase tracking-widest text-[#f87171] font-bold mb-4 flex items-center gap-2">
                            <Zap size={14} /> Transparency: Campaign Finance
                          </h3>
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                              <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                                <p className="text-[10px] text-textMuted uppercase font-bold mb-1">Total Raised</p>
                                <p className="text-lg font-bold text-white">${detail.finance.total_raised.toLocaleString()}</p>
                              </div>
                              <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                                <p className="text-[10px] text-textMuted uppercase font-bold mb-1">Total Spent</p>
                                <p className="text-lg font-bold text-white">${detail.finance.total_spent.toLocaleString()}</p>
                              </div>
                            </div>
                            <div className="bg-black/40 p-3 rounded-lg border border-white/5 flex justify-between items-center">
                              <div>
                                <p className="text-[10px] text-textMuted uppercase font-bold">Cash on Hand</p>
                                <p className="text-md font-bold text-success">${detail.finance.cash_on_hand.toLocaleString()}</p>
                              </div>
                              <button 
                                onClick={() => window.open(detail.finance.fec_url, '_blank')}
                                className="text-[10px] font-bold text-primary hover:underline"
                              >
                                VIEW FEC FILINGS
                              </button>
                            </div>
                            <p className="text-[10px] text-textMuted italic leading-tight">
                              Financial telemetry sourced from OpenFEC. Data represents the current 2024 election cycle.
                            </p>
                          </div>
                        </div>
                      )}

                      <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                        <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                          <Activity size={14} className="text-secondary" /> GovTrack Intelligence
                        </h3>
                        {govtrack ? (
                           <div className="bg-[#0d0d14] p-3 rounded-lg border border-white/5">
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-xs text-textMuted uppercase">Passage Prognosis:</span>
                                <span className="text-xs font-bold text-secondary">
                                  {(govtrack.current_prognosis === 'high' || govtrack.current_prognosis === 'very_high') ? 'PROBABLE' : 'UNLIKELY'}
                                </span>
                              </div>
                              <p className="text-[10px] text-textMuted leading-relaxed">
                                {govtrack.is_alive ? "This bill is active. GovTrack calculates probability based on historical patterns." : "This session has concluded."}
                              </p>
                           </div>
                        ) : (
                          <p className="text-xs text-textMuted italic">No additional telemetry for this schema partition.</p>
                        )}
                      </div>

                      <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                        <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                          <CheckCircle size={14} /> Congressional Telemetry
                        </h3>
                        {/* ... existing votes ... */}
                        <div className="space-y-3">
                          {(detail.votes || []).length > 0 ? (detail.votes || []).map((v, idx) => (
                            <div key={idx} className="bg-[#0d0d14] p-3 rounded-lg border border-white/5">
                               <div className="flex justify-between items-center mb-2">
                                 <span className="text-sm font-bold text-white tracking-wide">{v.chamber} | {v.type}</span>
                                 <span className="text-xs text-textMuted">{v.date}</span>
                               </div>
                               <div className="flex items-center gap-4">
                                  <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-success"></span> <span className="text-xs text-white">Y: {v.yes}</span></div>
                                  <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500"></span> <span className="text-xs text-white">N: {v.no}</span></div>
                                  <span className="ml-auto text-xs font-bold text-success uppercase tracking-widest bg-success/10 px-2 py-0.5 rounded">{v.result}</span>
                               </div>
                            </div>
                          )) : (
                            <p className="text-xs text-textMuted italic">No recorded floor votes for this bill identity.</p>
                          )}
                        </div>
                      </div>

                      {fedReg.length > 0 && (
                        <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5">
                          <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                            <ExternalLink size={14} /> Related Agency Documents
                          </h3>
                          <div className="space-y-2">
                            {fedReg.map((doc, idx) => (
                              <div key={idx} className="text-[10px] text-white p-2 bg-white/5 rounded border border-white/5 hover:bg-white/10 cursor-pointer" onClick={() => window.open(doc.html_url, '_blank')}>
                                <span className="block font-bold text-textMuted truncate">{doc.agencies?.[0]}</span>
                                <span className="line-clamp-1">{doc.title}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

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
