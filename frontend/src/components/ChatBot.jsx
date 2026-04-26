import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Bot, User } from 'lucide-react';
import MarkdownIt from 'markdown-it';
import API_BASE_URL from '../api_config';

const mdParser = new MarkdownIt();

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Hello! I am your local GraphRAG Policy Assistant. Ask me anything about current legislation.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/agent/quick-chat`, { query: userMessage.content });
      setMessages(prev => [...prev, { role: 'system', content: response.data.reply }]);
    } catch (err) {
      console.error("Chat error", err);
      setMessages(prev => [...prev, { role: 'system', content: "*Error connecting to RAG agent. Ensure backend is running.*" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <button 
              onClick={() => setIsOpen(true)}
              className="bg-primary hover:bg-secondary text-white p-4 rounded-full shadow-2xl flex items-center justify-center transition-colors group relative border border-white/20"
            >
              <div className="absolute inset-0 bg-primary/40 rounded-full blur-xl group-hover:bg-secondary/40 transition-colors"></div>
              <MessageSquare size={24} className="relative z-10" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 z-50 w-80 md:w-96 bg-[#12121c] border border-primary/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
            style={{ height: '500px' }}
          >
            {/* Header */}
            <div className="bg-primary border-b border-white/10 p-4 flex justify-between items-center shadow-lg relative z-10">
              <div className="flex items-center gap-2">
                <Bot size={20} className="text-white" />
                <h3 className="font-bold text-white tracking-wide">RAG Policy Assistant</h3>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-white/70 hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-gradient-to-b from-primary/5 to-transparent">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'system' && (
                     <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/30">
                       <Bot size={16} className="text-primary" />
                     </div>
                  )}
                  <div className={`p-3 rounded-xl max-w-[80%] text-sm ${
                    msg.role === 'user' 
                      ? 'bg-secondary text-white rounded-tr-sm shadow-md' 
                      : 'bg-white/5 border border-white/10 text-textMain rounded-tl-sm shadow-sm'
                  }`}>
                     {msg.role === 'user' ? (
                        msg.content
                     ) : (
                        <div className="markdown-body text-sm chat-markdown" dangerouslySetInnerHTML={{ __html: mdParser.render(msg.content) }} />
                     )}
                  </div>
                  {msg.role === 'user' && (
                     <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center shrink-0 border border-secondary/30">
                       <User size={16} className="text-secondary" />
                     </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3 justify-start">
                   <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/30">
                     <Bot size={16} className="text-primary" />
                   </div>
                   <div className="p-3 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2">
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></span>
                   </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-[#181824] border-t border-white/10">
              <form 
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="flex items-center gap-2"
              >
                <input 
                  type="text" 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question..."
                  className="flex-1 bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-primary/50 transition-colors"
                />
                <button 
                  type="submit" 
                  disabled={loading || !input.trim()}
                  className="bg-primary hover:bg-secondary text-white p-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={18} />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
