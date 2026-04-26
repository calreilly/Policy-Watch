export default function TrustScore({ score }) {
  const percentage = Math.round(score * 100);
  
  let color = 'var(--success)';
  if (percentage < 70) color = '#f59e0b';
  if (percentage < 50) color = '#ef4444';

  return (
    <div style={{ 
      display: 'flex', alignItems: 'center', gap: '0.75rem',
      background: 'rgba(0,0,0,0.4)', padding: '0.5rem 1rem', borderRadius: '20px',
      border: `1px solid ${color}`
    }}>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Trust Score</div>
      <div style={{ color, fontWeight: 700, fontSize: '1.1rem' }}>{percentage}%</div>
    </div>
  );
}
