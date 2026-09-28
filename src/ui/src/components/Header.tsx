type HeaderProps = {
  title: string;
  subtitle?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function Header({ title, subtitle, actionLabel = 'Interface', onAction }: HeaderProps) {
  return (
    <header className="page-header">
      <div>
        {subtitle ? <p className="header-kicker">{subtitle}</p> : null}
        <h1>{title}</h1>
      </div>

      <button type="button" className="primary-btn small" onClick={onAction}>
        {actionLabel}
      </button>
    </header>
  );
}
