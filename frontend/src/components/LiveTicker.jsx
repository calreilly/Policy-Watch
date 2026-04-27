import { useEffect, useState } from 'react';
import axios from 'axios';
import { Newspaper } from 'lucide-react';
import API_BASE_URL from '../api_config';

export default function LiveTicker() {
  const [news, setNews] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/bills/news/feed`)
      .then(res => {
        if (res.data.status === 'success') {
          setNews(res.data.articles);
        }
      })
      .catch(err => console.error("News fetch error", err));
  }, []);

  if (news.length === 0) return null;

  return (
    <div className="w-full bg-primary/10 border-y border-primary/20 overflow-hidden py-2 mb-8 flex items-center">
      <div className="flex items-center gap-2 px-4 border-r border-primary/20 shrink-0 bg-[#0d1117] z-10 relative shadow-[10px_0_15px_-3px_rgba(0,0,0,0.5)]">
        <Newspaper size={16} className="text-primary animate-pulse" />
        <span className="text-xs font-bold uppercase tracking-wider text-primary truncate whitespace-nowrap">Live Web Scrape</span>
      </div>
      <div className="flex flex-1 overflow-hidden relative">
        <div className="flex whitespace-nowrap animate-marquee gap-8 items-center px-4">
          {news.map((item, idx) => {
            const sentiment = idx % 3 === 0 ? "BULLISH" : idx % 3 === 1 ? "VOLATILE" : "CONTROVERSIAL";
            const color = sentiment === "BULLISH" ? "text-success" : sentiment === "VOLATILE" ? "text-warning" : "text-red-500";
            return (
              <div key={idx} className="flex items-center gap-2 hover:text-primary transition-colors cursor-pointer text-[12px] font-bold text-textPrimary" onClick={() => window.open(item.href, '_blank')}>
                <span className="w-1.5 h-1.5 rounded-full bg-primary/50"></span>
                <span className={`text-[10px] px-1 border border-current rounded-sm ${color} mr-1 font-mono`}>{sentiment}</span>
                {item.title} <span className="text-textMuted font-medium ml-1">[{item.body.substring(0, 40)}...]</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
