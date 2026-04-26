import { motion } from 'framer-motion';
import { Calendar, FileText, Activity, ExternalLink } from 'lucide-react';

export default function BillCard({ bill, index = 0, onSelect }) {
  const formatDate = (d) => {
    if (!d) return 'N/A';
    try {
      return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch { return d; }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      onClick={() => onSelect && onSelect(bill.id)}
      className="glass-panel p-6 group hover:border-primary/50 relative overflow-hidden flex flex-col cursor-pointer"
    >
      {/* Accent bar */}
      <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-primary to-secondary transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></div>
      
      {/* Header: ID badge + status */}
      <div className="flex justify-between items-start mb-3 gap-2">
        <div className="px-2.5 py-1 bg-primary/10 text-primary rounded-full text-[11px] font-bold border border-primary/20 tracking-wider shrink-0">
          {bill.id}
        </div>
      </div>
      
      {/* Title */}
      <h3 className="text-base font-bold text-white mb-3 group-hover:text-primary transition-colors duration-300 line-clamp-3 leading-snug">
        {bill.title}
      </h3>
      
      {/* Latest action */}
      {bill.latest_action && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-white/[0.03] border border-border/50 text-xs text-textMuted leading-relaxed line-clamp-2">
          <span className="text-success font-semibold mr-1">Latest:</span>
          {bill.latest_action}
        </div>
      )}
      
      {/* Status badge */}
      {bill.status && (
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-success/10 text-success rounded-full text-[10px] font-bold border border-success/20 self-start mb-4 line-clamp-1 max-w-full overflow-hidden">
          <Activity size={10} className="shrink-0" />
          <span className="truncate">{bill.status}</span>
        </div>
      )}
      
      {/* Footer */}
      <div className="flex items-center justify-between gap-4 text-textMuted text-xs mt-auto pt-3 border-t border-border/50">
        <div className="flex items-center gap-1.5">
          <Calendar size={12} className="text-primary/70" />
          <span>{formatDate(bill.introduced_date)}</span>
        </div>
        {bill.url && (
          <a href={bill.url} target="_blank" rel="noopener noreferrer"
             onClick={(e) => e.stopPropagation()}
             className="flex items-center gap-1 text-primary/70 hover:text-primary transition-colors z-10 relative">
            <ExternalLink size={12} />
            <span>Source</span>
          </a>
        )}
      </div>
    </motion.div>
  );
}
