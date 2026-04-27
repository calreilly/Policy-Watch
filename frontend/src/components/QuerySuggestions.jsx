import React from 'react';
import { Sparkles, TrendingUp, ShieldCheck } from 'lucide-react';

const SUGGESTIONS = [
  { id: 1, text: "AI regulation in the 118th Congress", icon: <TrendingUp size={14} /> },
  { id: 2, text: "Healthcare affordability and drug pricing", icon: <ShieldCheck size={14} /> },
  { id: 3, text: "Climate change and clean energy initiatives", icon: <Sparkles size={14} /> },
  { id: 4, text: "Military budget and defense appropriations", icon: <TrendingUp size={14} /> },
];

const QuerySuggestions = ({ onSelect }) => {
  return (
    <div className="flex flex-wrap gap-2 mt-4">
      {SUGGESTIONS.map((s) => (
        <button
          key={s.id}
          onClick={() => onSelect(s.text)}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-xs text-gray-400 hover:text-white transition-all transform hover:scale-105 active:scale-95"
        >
          {s.icon}
          {s.text}
        </button>
      ))}
    </div>
  );
};

export default QuerySuggestions;
