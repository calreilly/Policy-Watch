import { useState } from 'react';
import axios from 'axios';
import BillCard from '../components/BillCard';
import { SearchIcon, Loader2 } from 'lucide-react';
import API_BASE_URL from '../api_config';

export default function BillSearch() {
  const [query, setQuery] = useState('');
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/bills/search?q=${encodeURIComponent(query)}`);
      setBills(response.data.bills || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-10">
      <div className="max-w-3xl">
        <h1 className="text-4xl font-extrabold tracking-tight mb-4 text-white">Registry Search</h1>
        <p className="text-textMuted text-lg mb-8">Utilize vector similarity and BM25 heuristic algorithms to locate specific legislative materials within the database.</p>
        
        <form onSubmit={handleSearch} className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <SearchIcon className="h-5 w-5 text-primary group-focus-within:text-secondary transition-colors" />
          </div>
          <input 
            type="text" 
            placeholder="e.g. Content moderation guidelines, Budget caps..." 
            className="input-styled pl-12 pr-32 text-lg"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button 
            type="submit" 
            className="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-primary to-secondary px-6 rounded-lg font-semibold text-white hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
            disabled={loading}
          >
            {loading ? <><Loader2 className="animate-spin" size={18}/> Hunting</> : 'Search'}
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {searched && !loading && bills.length === 0 && (
          <div className="col-span-full py-12 text-center text-textMuted bg-black/20 rounded-2xl border border-border border-dashed">
            <p className="text-lg">No regulatory bills found matching those exact vectors.</p>
          </div>
        )}
        {bills.map((bill, i) => (
          <BillCard key={bill.id} bill={bill} index={i} />
        ))}
      </div>
    </div>
  );
}
