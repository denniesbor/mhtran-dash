// Role: persistent page chrome — header + main content area
// Author: Dennies Bor

import { Link, NavLink } from "react-router-dom";

export default function Shell({ children }) {
  return (
    <div className="flex flex-col h-full bg-surface">
      <header className="flex items-center justify-between px-6 py-3 border-b border-line bg-surface-raised shrink-0">
        <Link to="/" className="flex flex-col leading-tight">
          <span className="text-sm font-semibold text-ink tracking-tight">
            Multi-Hazard Transmission
          </span>
          <span className="text-[10px] text-ink-muted tracking-wide uppercase">
            US Grid Risk Explorer
          </span>
        </Link>
        <nav className="flex gap-4 text-sm">
          <NavLink
            to="/map"
            className={({ isActive }) =>
              isActive ? "text-accent font-medium" : "text-ink-muted hover:text-ink"
            }
          >
            Map
          </NavLink>
          <NavLink
            to="/compare"
            className={({ isActive }) =>
              isActive ? "text-accent font-medium" : "text-ink-muted hover:text-ink"
            }
          >
            Compare
          </NavLink>
        </nav>
      </header>
      <main className="flex-1 min-h-0 overflow-hidden">{children}</main>
    </div>
  );
}
