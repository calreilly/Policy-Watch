import { useEffect, useState } from 'react';
import axios from 'axios';
import BillCard from '../components/BillCard';
import { RefreshCw, Zap } from 'lucide-react';
import NetworkGraph from '../components/NetworkGraph';
import LiveTicker from '../components/LiveTicker';
import BillModal from '../components/BillModal';
import API_BASE_URL from '../api_config';

export default function Dashboard() {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedBillId, setSelectedBillId] = useState(null);

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

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/bills/refresh`);
      if (res.data.new > 0 || res.data.updated > 0) {
          alert(`Success: Synced ${res.data.new} new bills and updated ${res.data.updated} records!`);
      } else {
          alert("Database already globally up-to-date with current Congress events.");
      }
      await fetchBills();
    } catch (err) {
      if (err.response && err.response.status === 429) {
          alert("Congress.gov API Rate Limit Reached! Cannot sync new bills right now. Try again later.");
      } else {
          console.error("Refresh err", err);
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchBills(); }, []);

  return (
    <div className="space-y-8">
      <NetworkGraph />
      <LiveTicker />
      
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
      
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="glass-panel h-48 animate-pulse-slow"></div>
          ))}
        </div>
      ) : bills.length === 0 ? (
        <div className="glass-panel p-12 text-center">
          <p className="text-textMuted text-lg">No bills loaded yet. Click "Refresh Data" to sync from Congress.gov.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {bills.map((b, idx) => {
            return (
              <BillCard 
                key={b.id || idx} 
                bill={b} 
                index={idx} 
                onSelect={(id) => setSelectedBillId(id)}
              />
            );
          })}
        </div>
      )}
      
      {/* Dynamic Modal Overlay */}
      <BillModal billId={selectedBillId} onClose={() => setSelectedBillId(null)} />
    </div>
  );
}
