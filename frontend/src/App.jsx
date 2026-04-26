import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, LayoutDashboard, FileText, ChevronRight } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import BillSearch from './pages/BillSearch';
import BriefGenerator from './pages/BriefGenerator';
import ChatBot from './components/ChatBot';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'search', label: 'Search Bills', icon: Search },
    { id: 'brief', label: 'Brief Generator', icon: FileText }
  ];

  return (
    <div className="flex min-h-screen">
      {/* Advanced Sidebar Navigation */}
      <motion.aside 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        className="w-64 glass-panel m-4 flex flex-col justify-between hidden md:flex sticky top-4 h-[calc(100vh-2rem)]"
      >
        <div className="p-6">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
              <span className="font-bold text-lg text-white">PW</span>
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-textMuted">
              PolicyWatch
            </h1>
          </div>
          
          <nav className="space-y-2">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 ${
                  currentPage === item.id 
                    ? 'bg-primary/10 text-primary border border-primary/20 shadow-inner' 
                    : 'text-textMuted hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon size={18} className={currentPage === item.id ? 'text-primary' : 'text-textMuted'} />
                  <span className="font-medium">{item.label}</span>
                </div>
                {currentPage === item.id && <ChevronRight size={16} className="opacity-50" />}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="p-6 border-t border-border/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center border border-white/5">
              <span className="text-sm font-semibold text-white">US</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">Gov API</span>
              <span className="text-xs text-success flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-success"></span> Online
              </span>
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto overflow-y-auto">
        {/* Mobile Header (Hidden on MD+) */}
        <div className="md:hidden flex items-center justify-between glass-panel p-4 mb-6">
          <h1 className="font-bold text-xl text-primary">PolicyWatch</h1>
          <select 
            className="bg-black/40 border border-border rounded-lg px-3 py-2 outline-none"
            value={currentPage}
            onChange={(e) => setCurrentPage(e.target.value)}
          >
            {navItems.map(i => <option key={i.id} value={i.id}>{i.label}</option>)}
          </select>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="h-full relative"
          >
            {currentPage === 'dashboard' && <Dashboard />}
            {currentPage === 'search' && <BillSearch />}
            {currentPage === 'brief' && <BriefGenerator />}
          </motion.div>
        </AnimatePresence>
        
        {/* Global ChatBot Mount */}
        <ChatBot />
      </main>
    </div>
  );
}
