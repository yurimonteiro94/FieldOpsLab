import type { PageId } from "../domain/platform";

interface LayoutProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  children: React.ReactNode;
}

const navItems: Array<{ id: PageId; label: string }> = [
  {
    id: "dashboard",
    label: "Dashboard",
  },
  {
    id: "reports",
    label: "Reports",
  },
  {
    id: "scientific-validation",
    label: "Scientific validation",
  },
];

export function Layout({ activePage, onNavigate, children }: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">FieldOps Lab</p>
          <h1>Research platform</h1>
          <p className="sidebar-copy">
            Read-only local interface for inspecting platform status, generated
            artifacts, and scientific validation risks.
          </p>
        </div>

        <nav aria-label="Main navigation" className="nav-list">
          {navItems.map((item) => (
            <button
              className={item.id === activePage ? "nav-item active" : "nav-item"}
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <strong>Safety mode</strong>
          <span>Read-only. No backend operation trigger is exposed here.</span>
        </div>
      </aside>

      <main className="page-shell">{children}</main>
    </div>
  );
}