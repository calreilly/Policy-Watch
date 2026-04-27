import { useEffect, useState } from 'react';
import axios from 'axios';
import BillCard from '../components/BillCard';
import { RefreshCw, Zap, Activity } from 'lucide-react';
import NetworkGraph from '../components/NetworkGraph';
import LiveTicker from '../components/LiveTicker';
import BillModal from '../components/BillModal';
import API_BASE_URL from '../api_config';

export default function Dashboard() {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedBillId, setSelectedBillId] = useState(null);
  const [evalResults, setEvalResults] = useState(null);
  const [agencyActions, setAgencyActions] = useState([]);

  const fetchBills = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/bills/today`);
      setBills(response.data.bills || []);
    } catch (err) {
      console.error("Dashboard err", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchExtraIntelligence = async () => {
    try {
      const [evalRes, agencyRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/evaluation/results`).catch(() => null),
        axios.get(`${API_BASE_URL}/api/federal-register/recent-rules?limit=3`).catch(() => null)
      ]);
      if (evalRes?.data?.status === 'success') setEvalResults(evalRes.data.results);
      if (agencyRes?.data?.status === 'success') setAgencyActions(agencyRes.data.results);
    } catch (err) {
      console.error("Extra intel err", err);
    }
  };

  const runEvaluation = async () => {
    try {
      setRefreshing(true);
      const res = await axios.get(`${API_BASE_URL}/api/evaluation/run`);
      setEvalResults(res.data.results);
      alert("Evaluation Complete! RAG accuracy metrics updated.");
    } catch (err) {
      console.error("Eval run err", err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/bills/refresh`);
      if (res.data.status === 'rate_limited') {
        alert(`⚠️ Congress.gov is rate-limited right now. Showing ${res.data.total_bills} cached bills.`);
      } else if (res.data.new > 0 || res.data.updated > 0) {
        alert(`✅ Synced ${res.data.new} new bills and updated ${res.data.updated} existing records!`);
      } else {
        alert(`ℹ️ Database is already up-to-date (${res.data.total_bills} bills).`);
      }
      await fetchBills();
    } catch (err) {
      console.error("Refresh err", err);
      alert("Failed to contact the backend. Is the server running?");
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { 
    fetchBills(); 
    fetchExtraIntelligence();
  }, []);

  return (
    <div className="space-y-8">
      <NetworkGraph />
      <LiveTicker />
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Zap size={16} className="text-primary animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-widest text-primary">Live from Congress.gov</span>
              </div>
              <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-textMuted tracking-tight mb-2">Legislative Pulse</h1>
              <p className="text-textMuted text-lg max-w-2xl">Real-time feed of the most recently updated bills in the 119th Congress.</p>
            </div>
            <button 
              onClick={handleRefresh}
              disabled={refreshing}
              className="btn-primary flex items-center gap-2 text-sm shrink-0 self-start md:self-end"
            >
              <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              {refreshing ? 'Syncing Congress.gov...' : 'Refresh Data'}
            </button>
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/5 bg-white/5">
           <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-3 flex items-center gap-2">
             <Activity size={14} /> System Health (Week 7)
           </h3>
           {evalResults ? (
             <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-textMuted">RAG MRR:</span>
                  <span className="text-success font-bold">{(evalResults.mean_mrr * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-textMuted">RAG NDCG:</span>
                  <span className="text-success font-bold">{(evalResults.mean_ndcg * 100).toFixed(1)}%</span>
                </div>
                <button onClick={runEvaluation} className="w-full mt-2 text-[10px] text-primary hover:text-white uppercase tracking-tighter transition-colors">Re-run Benchmark</button>
             </div>
           ) : (
             <button onClick={runEvaluation} className="w-full py-2 bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold uppercase rounded hover:bg-primary/20 transition-all">Evaluate RAG Performance</button>
           )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <div className="xl:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-6">
          {loading ? (
            [1,2,3,4].map(i => (
              <div key={i} className="glass-panel h-48 animate-pulse-slow"></div>
            ))
          ) : bills.length === 0 ? (
            <div className="col-span-2 glass-panel p-12 text-center">
              <p className="text-textMuted text-lg">No bills loaded yet.</p>
            </div>
          ) : (
            bills.slice(0, 6).map((b, idx) => (
              <BillCard 
                key={b.id || idx} 
                bill={b} 
                index={idx} 
                onSelect={(id) => setSelectedBillId(id)}
              />
            ))
          )}
        </div>

        <div className="xl:col-span-2 space-y-6">
           <div className="glass-panel p-5 rounded-xl border border-white/5 bg-white/5 h-full">
              <h3 className="text-xs uppercase tracking-widest text-textMuted font-bold mb-4 flex items-center gap-2">
                <Zap size={14} className="text-secondary" /> Agency Action (Federal Register)
              </h3>
              <div className="space-y-4">
                {agencyActions.length > 0 ? agencyActions.map((rule, idx) => (
                  <div key={idx} className="bg-black/20 p-3 rounded-lg border border-white/5 hover:border-secondary/30 transition-all cursor-pointer" onClick={() => window.open(rule.html_url, '_blank')}>
                    <p className="text-xs font-bold text-secondary mb-1">{rule.agencies?.[0]}</p>
                    <p className="text-sm text-white font-medium line-clamp-2 mb-2">{rule.title}</p>
                    <p className="text-[10px] text-textMuted">{rule.publication_date}</p>
                  </div>
                )) : (
                  <p className="text-xs text-textMuted italic">No recent agency rules found.</p>
                )}
              </div>
           </div>
        </div>
      </div>
      
      {/* Dynamic Modal Overlay */}
      {selectedBillId && (
        <BillModal billId={selectedBillId} onClose={() => setSelectedBillId(null)} />
      )}
    </div>
  );
}
