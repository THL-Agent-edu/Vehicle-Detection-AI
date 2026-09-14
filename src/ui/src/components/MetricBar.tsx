type MetricBarProps = {
  label: string;
  value: number;
  color?: string;
};

export function MetricBar({ label, value, color = '#2563eb' }: MetricBarProps) {
  return (
    <div className="metric-row">
      <div className="metric-meta">
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="metric-track">
        <span style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}
