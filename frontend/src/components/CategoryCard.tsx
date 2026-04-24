import { Link } from "react-router-dom";
import {
  Activity,
  Film,
  Image as ImageIcon,
  Mic,
  Sparkles,
  Type,
  User,
  type LucideIcon,
} from "lucide-react";
import type { CategorySummary } from "../lib/types";

const ICONS: Record<string, LucideIcon> = {
  mic: Mic,
  type: Type,
  image: ImageIcon,
  user: User,
  activity: Activity,
  film: Film,
  sparkles: Sparkles,
};

export default function CategoryCard({ cat }: { cat: CategorySummary }) {
  const Icon = ICONS[cat.icon ?? ""] ?? Sparkles;
  return (
    <Link
      to={`/c/${cat.id}`}
      className="card group relative flex flex-col gap-3 p-5 transition hover:border-accent/60 hover:bg-ink-900"
    >
      <div className="flex items-center justify-between">
        <div className="grid h-10 w-10 place-items-center rounded-lg bg-accent/20 text-accent-muted">
          <Icon size={20} />
        </div>
        <span className="chip">{cat.model_count} models</span>
      </div>
      <div>
        <div className="text-base font-semibold text-ink-100">{cat.title}</div>
        <div className="mt-1 text-sm text-ink-400">{cat.subtitle}</div>
      </div>
      <div className="mt-2 text-xs text-accent-muted opacity-0 transition group-hover:opacity-100">
        Browse models →
      </div>
    </Link>
  );
}
