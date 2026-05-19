import type { ReactNode } from "react";

import type { PageId } from "../domain/platform";

interface LayoutProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  children: ReactNode;
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
    id: "experimental-design",
    label: "Experimental design",
  },
  {
    id: "scientific-validation",
    label: "Scientific validation",
  },
  {
    id: "research-method",
    label: "Research method",
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
            artifacts, research framing, experimental design, and scientific
            validation risks.
          </p>

          <nav className="nav-list" aria-label="FieldOps Lab pages">
            {navItems.map((item) => (
              <button
                className={`nav-item ${activePage === item.id ? "active" : ""}`}
                key={item.id}
                onClick={() => onNavigate(item.id)}
                type="button"
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="sidebar-footer">
          <strong>Safety mode</strong>
          <span>Read-only. No backend operation trigger is exposed here.</span>
        </div>
      </aside>

      <main className="page-shell">{children}</main>
    </div>
  );
}