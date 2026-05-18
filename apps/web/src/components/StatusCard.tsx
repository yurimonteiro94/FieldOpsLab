interface StatusCardProps {
  title: string;
  value: string;
  description: string;
}

export function StatusCard({ title, value, description }: StatusCardProps) {
  return (
    <article className="status-card">
      <p className="card-title">{title}</p>
      <strong>{value}</strong>
      <p>{description}</p>
    </article>
  );
}