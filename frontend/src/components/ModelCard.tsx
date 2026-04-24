import { Link } from "react-router-dom";
import { CheckCircle2, Cpu, Download, HardDrive } from "lucide-react";
import type { InstallState, ModelSpec } from "../lib/types";

const STATUS_TONE: Record<ModelSpec["status"], string> = {
  stable: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  beta: "bg-sky-500/10 text-sky-400 border-sky-500/30",
  experimental: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  planned: "bg-ink-800 text-ink-400 border-ink-700",
};

export default function ModelCard({
  model,
  install,
}: {
  model: ModelSpec;
  install?: InstallState;
}) {
  const installed = install?.status === "installed";
  const sizeGb = model.weights.reduce(
    (s, w) => s + (w.approx_size_gb ?? 0),
    0,
  );

  return (
    <Link
      to={`/m/${model.id}`}
      className="card group flex flex-col gap-3 p-5 transition hover:border-accent/60 hover:bg-ink-900"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-base font-semibold text-ink-100">
            {model.name}
          </div>
          <div className="mt-1 line-clamp-2 text-sm text-ink-400">
            {model.short_description}
          </div>
        </div>
        <span
          className={`shrink-0 rounded-full border px-2 py-0.5 text-xs ${STATUS_TONE[model.status]}`}
        >
          {model.status}
        </span>
      </div>
      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-ink-400">
        <span className="chip">
          <Cpu size={12} /> {model.vram_gb_recommended} GB VRAM
        </span>
        {sizeGb > 0 && (
          <span className="chip">
            <HardDrive size={12} /> {sizeGb.toFixed(1)} GB weights
          </span>
        )}
        <span className="chip">{model.license}</span>
        {model.tags.slice(0, 2).map((t) => (
          <span key={t} className="chip-accent">
            {t}
          </span>
        ))}
      </div>
      <div className="mt-1 flex items-center justify-between text-xs">
        <span className="text-ink-500">{model.id}</span>
        <span className="flex items-center gap-1 text-ink-400">
          {installed ? (
            <>
              <CheckCircle2 size={14} className="text-emerald-400" />
              Installed
            </>
          ) : (
            <>
              <Download size={14} />
              Not installed
            </>
          )}
        </span>
      </div>
    </Link>
  );
}
