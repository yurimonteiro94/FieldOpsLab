import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">FieldOps Lab</p>
          <h1>Read-only research platform dashboard</h1>
        </div>
        <span className="mode-badge">Read-only</span>
      </header>

      <main>{children}</main>
    </div>
  );
}