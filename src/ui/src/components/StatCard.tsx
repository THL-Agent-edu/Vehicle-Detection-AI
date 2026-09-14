type StatCardProps = {
  label: string;
  value: string;
  delta?: string;
  tone?: 'blue' | 'green' | 'amber' | 'gray';
};

export function StatCard({ label, value, delta, tone = 'blue' }: StatCardProps) {
  return (
    <div className={`stat-card ${tone}`}>
      <div className="stat-card-topline">
        <span className="stat-label">{label}</span>
        {delta ? <span className="stat-delta">{delta}</span> : null}
      </div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
