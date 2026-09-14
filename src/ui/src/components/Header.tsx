type HeaderProps = {
  title: string;
  subtitle?: string;
  actionLabel?: string;
};

export function Header({ title, subtitle, actionLabel = 'Interface' }: HeaderProps) {
  return (
    <header className="page-header">
      <div>
        {subtitle ? <p className="header-kicker">{subtitle}</p> : null}
        <h1>{title}</h1>
      </div>

      <button type="button" className="primary-btn small">
        {actionLabel}
      </button>
    </header>
  );
}
