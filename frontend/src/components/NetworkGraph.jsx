import { useEffect, useRef, useState, useCallback, memo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Network } from 'lucide-react';

const NetworkGraph = memo(() => {
  const [data, setData] = useState({ nodes: [], links: [] });
  const graphRef = useRef();

  useEffect(() => {
    axios.get('http://127.0.0.1:8001/api/agent/graph-data')
      .then(res => {
        setData(res.data);
      })
      .catch(err => console.error("Graph fetch error", err));
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-panel overflow-hidden relative mb-8"
      style={{ height: '350px' }}
    >
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-full border border-white/10">
        <Network size={14} className="text-primary" />
        <span className="text-xs font-bold text-white tracking-widest uppercase">Neo4j Global Context Graph</span>
      </div>
      
      {data.nodes.length > 0 ? (
        <ForceGraph2D
          ref={graphRef}
          graphData={data}
          width={1200}
          height={350}
          backgroundColor="#00000000"
          nodeColor={node => node.group === 'Bill' ? '#10b981' : '#6366f1'}
          nodeRelSize={6}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          linkColor={() => 'rgba(255,255,255,0.1)'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

            ctx.fillStyle = node.group === 'Bill' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.2)';
            ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = node.group === 'Bill' ? '#10b981' : '#6366f1';
            ctx.fillText(label, node.x, node.y);
          }}
          onEngineStop={() => {
              if (graphRef.current) {
                 graphRef.current.zoomToFit(400, 50);
              }
          }}
        />
      ) : (
        <div className="w-full h-full flex flex-col items-center justify-center">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-textMuted text-xs font-semibold">Traversing Neo4j Nodes...</p>
        </div>
      )}
    </motion.div>
  );
});

export default NetworkGraph;
