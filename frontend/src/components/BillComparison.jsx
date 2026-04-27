import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Columns, ArrowRightLeft, ShieldAlert, CheckCircle, Info } from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../api_config';

const BillComparison = ({ selectedBills = [] }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (selectedBills.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/comparison/compare-bills`, {
        bill_ids: selectedBills.map(b => b.id)
      });
      setComparisonData(response.data.comparisons);
    } catch (err) {
      console.error('Comparison error:', err);
      setError('Failed to load comparative analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (selectedBills.length < 2) {
    return (
      <div className="p-8 text-center bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl">
        <Columns className="w-12 h-12 mx-auto text-blue-400 mb-4 opacity-50" />
        <p className="text-gray-400">Select at least two bills from the explorer to perform a comparative impact analysis.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between bg-white/5 p-4 rounded-xl border border-white/10">
        <div className="flex items-center gap-3">
          <ArrowRightLeft className="text-blue-400" />
          <span className="text-sm font-medium text-white">Comparing {selectedBills.length} Legislative Items</span>
        </div>
        <button
          onClick={handleCompare}
          disabled={loading}
          className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-lg font-bold shadow-lg shadow-blue-900/20 transition-all disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Generate Comparative Report'}
        </button>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200 text-sm flex items-center gap-3"
          >
            <ShieldAlert size={18} />
            {error}
          </motion.div>
        )}

        {comparisonData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {Object.entries(comparisonData).map(([id, data]) => (
              <div key={id} className="bg-white/5 rounded-2xl border border-white/10 overflow-hidden flex flex-col">
                <div className="p-6 border-b border-white/10 bg-white/5">
                  <h3 className="text-lg font-bold text-white mb-1">{data.title}</h3>
                  <span className="text-xs uppercase tracking-wider text-blue-400 font-bold bg-blue-500/10 px-2 py-1 rounded">
                    {data.status || 'Introduced'}
                  </span>
                </div>
                
                <div className="p-6 space-y-4 flex-grow">
                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                      <Columns size={12} /> IMPACTED SECTORS
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {(Array.isArray(data.impact?.sectors) ? data.impact.sectors : ["General"]).map(s => (
                        <span key={String(s)} className="px-2 py-1 bg-white/10 rounded text-xs text-gray-300 border border-white/10">
                          {String(s)}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                      <Info size={12} /> BUDGETARY IMPLICATIONS
                    </span>
                    <div className="text-sm text-gray-300 leading-relaxed bg-white/5 p-3 rounded-lg">
                      {typeof data.impact?.budgetary_impact === 'object' 
                        ? JSON.stringify(data.impact.budgetary_impact) 
                        : String(data.impact?.budgetary_impact || "N/A")}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                      <CheckCircle size={12} /> TIMELINE
                    </span>
                    <p className="text-sm text-gray-400">{data.impact?.timeline || "Unknown"}</p>
                  </div>

                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                      <ShieldAlert size={12} /> RISK ASSESSMENT
                    </span>
                    <p className="text-sm text-red-300/80 italic">
                      {typeof data.impact?.risks === 'object' 
                        ? JSON.stringify(data.impact.risks) 
                        : String(data.impact?.risks || "Unassessed")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BillComparison;
