type SidebarProps = {
  items: string[];
  activeItem: string;
  onSelect: (item: string) => void;
};

export function Sidebar({ items, activeItem, onSelect }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">V</div>
        <div>
          <div className="brand-name">V-AI SYSTEM</div>
          <div className="brand-subtitle">TRAFFIC INTELLIGENCE</div>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Sidebar navigation">
        {items.map((item) => (
          <button
            key={item}
            type="button"
            className={item === activeItem ? 'nav-item active' : 'nav-item'}
            onClick={() => onSelect(item)}
          >
            {item}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="system-pill">Online</span>
        <span>Camera feed active</span>
      </div>
    </aside>
  );
}
