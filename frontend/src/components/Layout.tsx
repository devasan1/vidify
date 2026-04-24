import { NavLink, Outlet } from "react-router-dom";
import { Boxes, Clock, Home, Package, Sparkles } from "lucide-react";

function navItemClass({ isActive }: { isActive: boolean }) {
  return [
    "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition",
    isActive
      ? "bg-accent/20 text-accent-muted"
      : "text-ink-400 hover:bg-ink-800 hover:text-ink-100",
  ].join(" ");
}

export default function Layout() {
  return (
    <div className="flex h-full min-h-screen">
      <aside className="flex w-60 shrink-0 flex-col border-r border-ink-800 bg-ink-950/80 p-4">
        <div className="mb-6 flex items-center gap-2 px-2">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-accent text-accent-fg">
            <Sparkles size={18} />
          </div>
          <div>
            <div className="text-sm font-semibold">Vidify</div>
            <div className="text-xs text-ink-500">local AI video studio</div>
          </div>
        </div>
        <nav className="flex flex-col gap-1">
          <NavLink to="/" end className={navItemClass}>
            <Home size={16} /> Home
          </NavLink>
          <NavLink to="/models" className={navItemClass}>
            <Boxes size={16} /> All models
          </NavLink>
          <NavLink to="/installed" className={navItemClass}>
            <Package size={16} /> Model manager
          </NavLink>
          <NavLink to="/jobs" className={navItemClass}>
            <Clock size={16} /> Jobs
          </NavLink>
        </nav>
        <div className="mt-auto px-2 pt-6 text-xs text-ink-500">
          <div>localhost · open-source</div>
          <div className="mt-1">
            <a
              href="https://github.com/devasan1/vidify"
              target="_blank"
              rel="noreferrer"
              className="hover:text-accent-muted"
            >
              GitHub ↗
            </a>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
