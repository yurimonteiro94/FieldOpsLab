interface StatusCardProps {
  label: string;
  value: string;
  detail?: string;
}

export function StatusCard({ label, value, detail }: StatusCardProps) {
  return (
    <article className="status-card">
      <span className="status-label">{label}</span>
      <strong>{value}</strong>
      {detail ? <p>{detail}</p> : null}
    </article>
  );
}