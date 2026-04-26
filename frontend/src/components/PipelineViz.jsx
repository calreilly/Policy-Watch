export default function PipelineViz({ trace }) {
  if (!trace || trace.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {trace.map((step, idx) => (
        <div key={idx} style={{ position: 'relative' }}>
          <div style={{ display: 'flex', gap: '1rem', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '12px', border: '1px solid var(--glass-border)', zIndex: 2, position: 'relative' }}>
            <div style={{ 
              width: '32px', height: '32px', borderRadius: '50%', 
              background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', 
              display: 'flex', alignItems: 'center', justifyContent: 'center', 
              fontWeight: 'bold', fontSize: '1rem', flexShrink: 0
            }}>
              {step.step}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent-primary)', fontSize: '0.9rem' }}>{step.action}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{step.details}</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)', marginTop: '0.2rem' }}>{(step.duration_ms / 1000).toFixed(2)}s</div>
            </div>
          </div>
          {idx < trace.length - 1 && (
            <div style={{ 
              position: 'absolute', left: '16px', top: '48px', bottom: '-16px', 
              width: '2px', background: 'var(--accent-primary)', opacity: 0.3, zIndex: 1 
            }}></div>
          )}
        </div>
      ))}
    </div>
  );
}
